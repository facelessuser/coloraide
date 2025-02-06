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
from ..spaces import Space, LChish
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .cam16_jmh import Environment, cam16_to_xyz_d65, xyz_d65_to_cam16
from .lab import EPSILON, KAPPA, KE
from .lch import ACHROMATIC_THRESHOLD
from ..types import Vector
import math


def y_to_lstar(y: float) -> float:
    """Convert XYZ Y to Lab L*."""

    fy = alg.nth_root(y, 3) if y > EPSILON else (KAPPA * y + 16) / 116
    return (116.0 * fy) - 16.0


def lstar_to_y(lstar: float) -> float:
    """Convert Lab L* to XYZ Y."""

    fy = (lstar + 16) / 116
    y = fy ** 3 if lstar > KE else lstar / KAPPA
    return y


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

    h, c, t = coords[:]

    # Shortcut out for black
    if t == 0:
        return [0.0, 0.0, 0.0]

    # Calculate the Y we need to target
    y = lstar_to_y(t)

    # Try to start with a reasonable initial guess for J
    # Calculated by curve fitting J vs T.
    if t > 0:
        j = 0.00379058511492914 * t * t + 0.608983189401032 * t + 0.9155088574762233
    else:
        j = 9.514440756550361e-06 * t * t + 0.08693057439788597 * t -21.928975842194614

    epsilon = 2e-12

    maxiter = 16
    last = math.inf
    best = j
    xyz = [0.0] * 3

    # Try to find a J such that the returned y matches the returned y of the L*
    for _ in range(maxiter):
        prev = j
        xyz[:] = cam16_to_xyz_d65(J=j, C=c, h=h, env=env)

        # If we are within range, return XYZ
        # If we are closer than last time, save the values
        f0 = xyz[1] - y
        delta = abs(f0)

        if delta < epsilon:
            return xyz

        if delta < last:
            best = j
            last = delta

        # ```
        # f(j_root) = (j ** (1 / 2)) * 0.1
        # f(j) = ((f(j_root) * 100) ** 2) / j - 1 = 0
        # f(j_root) = Y = y / 100
        # f(j) = (y ** 2) / j - 1
        # f'(j) = (2 * y) / j
        # f'(j) = dx
        # j = j - f0 / dx
        # ```

        # Newton: 2nd order convergence
        # `dx` fraction is flipped so we can multiply by the derivative instead of divide
        j -= f0 * alg.zdiv(j, 2 * xyz[1])

        # If J is zero, the next round will yield zero
        # If values are too close, we'll be better off using bisect
        if j == 0 or abs(prev - j) < epsilon:  # pragma: no cover
            break


    # We could not acquire the precision we desired, return our closest attempt.
    xyz[:] = cam16_to_xyz_d65(J=best, C=c, h=h, env=env)

    # ```
    # if not converged:
    #     print('FAIL:', [h, c, t], xyz[1], y)
    # ```

    return xyz


def xyz_to_hct(coords: Vector, env: Environment) -> Vector:
    """Convert XYZ to HCT."""

    t = y_to_lstar(coords[1])
    if t == 0.0:
        return [0.0, 0.0, 0.0]
    c, h = xyz_d65_to_cam16(coords, env)[1:3]
    return [h, c, t]


class HCT(LChish, Space):
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
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE),
        Channel("c", 0.0, 145.0),
        Channel("t", 0.0, 100.0)
    )

    def normalize(self, coords: Vector) -> Vector:
        """Normalize."""

        if coords[1] < 0.0:
            return self.from_base(self.to_base(coords))
        coords[0] %= 360.0
        return coords

    def is_achromatic(self, coords: Vector) -> bool | None:
        """Check if color is achromatic."""

        # Account for both positive and negative chroma
        return coords[2] == 0 or abs(coords[1]) < ACHROMATIC_THRESHOLD

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
