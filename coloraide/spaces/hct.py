"""
HCT color space.

This implements the HCT color space as described. This is not a port of the Material library.
We simply, as described, create a color space with CIELAB L* and CAM16's C and h components.
Environment settings are calculated with the assumption of L* 50.

Generally, the HCT color space is restricted to sRGB and SDR range in the Material library, but we do
not have such restrictions.

Though we did not port HCT from Material Color Utilities, we did test against it, and are pretty
much on point. The only differences are due to matrix precision and white point precision. Material
uses an RGB <-> XYZ matrix that rounds values off significantly more than we do. Also, while we
calculate the XYZ points from the `xy` points without rounding, they have rounded XYZ points. Lastly,
the gamut mapping algorithm we use is likely different even though it arrives at pretty much the same
result, so slightly different values can occur.

Material:

```
> hct.Hct.fromInt(0xff305077)
Hct {
  argb: 4281356407,
  internalHue: 256.8040416857594,
  internalChroma: 31.761442797741243,
  internalTone: 33.34501410942328
}
```

ColorAide:

```
>>> from coloraide_extras.everything import ColorAll as Color
>>> Color('#305077').convert('hct')
color(--hct 256.79 31.766 33.344 / 1)
```

"""
from __future__ import annotations
from .. import algebra as alg
from .lch import LCh
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .cam16 import Environment, cam_to_xyz, xyz_to_cam
from .lab import y_to_lstar, lstar_to_y
from ..types import Vector
import math
from .. import util

# To obtain the first derivative for `J'`, we manually measure the rate of change
# at various points for `J` in relation to `y` in a CAM16 with the same environment
# that HCT uses. From this, it can be noted that if `dy / dJ` is divided by `y / J`,
# we get a fairly constant value (roughly between 1.8 - 2). From this, we have a
# rough approximation of `J' ~= K * y / J`, where we set `K` to measured average of
# `~1.832`.
#
# As it is possible for some colors to perform better if a different `K` is used,
# we employ Ostrowski's Method to further refine the Newton iteration which helps to
# compensates for any deviation and to converge on a more precise solution quicker.
K = 1.832
D65 = WHITES['2deg']['D65']


def hct_to_xyz(coords: Vector, env: Environment) -> Vector:
    """
    Convert HCT to XYZ.

    Use Newton's method to try and converge as quick as possible or converge as
    close as we can. While the requested precision is achieved most of the time,
    it may not always be achievable. Especially past the visible spectrum, the
    algorithm will likely struggle to get the same precision. If, for whatever
    reason, we cannot achieve the accuracy we seek in the allotted iterations,
    just return the closest we were able to get.
    """

    h, c, t = coords

    if t == 0 and c == 0:
        return [0.0, 0.0, 0.0]

    # Calculate the Y we need to target
    y = lstar_to_y(t)
    # Estimate J using assuming Y with an achromatic color.
    j = xyz_to_cam(util.xy_to_xyz(D65, Y=y), env=env)[0]

    epsilon = 1e-12
    maxiter = 8
    last = math.inf
    best = xyz = [0.0] * 3

    # Try to find a J such that the returned y matches the returned y of the L*
    for _ in range(maxiter):
        prev = j
        xyz = cam_to_xyz(J=j, C=c, h=h, env=env)
        f1 = xyz[1] - y

        delta = abs(f1)
        if delta < last:
            # If we are within range, return XYZ
            if delta < epsilon:
                return xyz

            # If we are closer than last time, save the values.
            # This is to ensure we take the best value when
            # iterations are struggling to find a good value,
            # e.g. Prophoto RGB in the blue region which is outside
            # the visible spectrum and the CAM16 algorithm breaks down.
            best = xyz
            last = delta

        # Newton: 2nd order convergence
        d1 = alg.zdiv(K * xyz[1], j)
        if abs(d1) < epsilon:
            break
        j -= f1 / d1

        # Ostrowski: 4th order convergence
        xyz2 = cam_to_xyz(J=j, C=c, h=h, env=env)
        f2 = xyz2[1] - y
        denom = f1 - 2 * f2
        if abs(denom) >= epsilon:  # pragma: no cover
            j -= f1 / denom * (f2 / d1)

        # Quit if there has been little to no change
        if abs(j - prev) < epsilon:  # pragma: no cover
            break

    # ```
    # print('FAIL:', [h, c, t], j, xyz[1], y)
    # ```

    return best


def xyz_to_hct(coords: Vector, env: Environment) -> Vector:
    """Convert XYZ to HCT."""

    t = y_to_lstar(coords[1])
    c, h = xyz_to_cam(coords, env)[1:3]
    return [h, c, t]


class HCT(LCh):
    """HCT class."""

    BASE = "xyz-d65"
    NAME = "hct"
    SERIALIZE = ("--hct",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(
        # D65 white point.
        white=WHITE,
        # 200 lux or `~11.72 cd/m2` multiplied by ~18.42%, a variation of gray world assumption.
        adapting_luminance=200 / math.pi * lstar_to_y(50.0),
        # A variation on gray world assumption: ~18.42% of reference white's `Yw == 100`.
        background_luminance=lstar_to_y(50.0) * 100,
        # Average surround.
        surround='average',
        # No discounting of illuminant.
        discounting=False
    )
    CHANNEL_ALIASES = {
        "lightness": "t",
        "tone": "t",
        "chroma": "c",
        "hue": "h"
    }

    CHANNELS = (
        Channel("h", flags=FLG_ANGLE),
        Channel("c", 0.0, 145.0),
        Channel("t", 0.0, 100.0)
    )

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "t"

    def normalize(self, coords: Vector) -> Vector:
        """Normalize."""

        if coords[1] < 0.0:
            return self.from_base(self.to_base(coords))
        coords[0] %= 360.0
        return coords

    def names(self) -> tuple[Channel, ...]:
        """Return LCh-ish names in the order L C h."""

        channels = self.channels
        return channels[2], channels[1], channels[0]

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from CAM16."""

        return hct_to_xyz(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16."""

        return xyz_to_hct(coords, self.ENV)
