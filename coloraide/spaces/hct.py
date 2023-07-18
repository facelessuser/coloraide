"""
HCT color space.

This implements the HCT color space as described. This is not a port of the Material library.
We simply, as described, create a color space with CIELAB L* and CAM16's C and h components.
Environment settings are calculated with the assumption of L* 50.

Our approach getting back to sRGB is likely different as we are using a simple binary search
to help calculate the missing piece (J) needed to convert CAM16 C and h back to XYZ such that
Y matches the L* conversion back to Y. I am certain the Material library is most likely
employing further tricks to resolve faster. We also try to get as good round trip as possible,
which forces us to probably make more iterations than Material does (none of this has been confirmed).

As ColorAide usually cares about setting powerless hues as NaN, especially for good interpolation,
we've also calculated the cut off for chromatic colors and will properly enforce achromatic,powerless
hues. This is because CAM16 actually resolves colors as achromatic before chroma reaches zero as
lightness increases. In the SDR range, a Tone of 100 will have a cut off as high as ~2.87 chroma.

Generally, the HCT color space is restricted to SDR range in the Material library, but we do not have
such restrictions.

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

Differences are inconsequential.
"""
from __future__ import annotations
from .. import algebra as alg
from .. import util
from ..spaces import Space, LChish
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .cam16_jmh import Environment, cam16_to_xyz_d65, xyz_d65_to_cam16
from .cam16_jmh import Achromatic as _Achromatic
from .srgb_linear import lin_srgb_to_xyz
from .srgb import lin_srgb
from .lab import EPSILON, KAPPA, KE
from ..types import Vector, VectorLike
from typing import Any
import math

ACHROMATIC_RESPONSE = [
    [0.06991457401674239, 0.14894004649491988, 209.54685746644427],
    [0.13982914803348123, 0.19600973408108388, 209.54683151374996],
    [0.20974372205022362, 0.22847588408235084, 209.54681244250116],
    [0.279658296066966, 0.2539510473857674, 209.54679680373425],
    [0.34957287008370486, 0.27520353123074354, 209.5467833054029],
    [0.6991457401674133, 0.3503388633000292, 209.54673233806605],
    [1.0487186102511181, 0.40138459372769575, 209.54669489478562],
    [1.398291480334823, 0.4411483978448841, 209.5466641968681],
    [1.7478643504185314, 0.4741765535239112, 209.54663770502128],
    [2.0974372205022362, 0.5026634742613167, 209.54661414586045],
    [2.447010090585941, 0.527852488793119, 209.5465927758291],
    [2.7965829606696495, 0.5505226723841257, 209.54657311722175],
    [3.1624547958278697, 0.5721193279495612, 209.54655401960414],
    [3.5553195764898433, 0.5933528830664249, 209.5465348955287],
    [3.9752712774319967, 0.6142212187429535, 209.5465157686296],
    [4.422818762249047, 0.6347462660662626, 209.54649663922487],
    [4.89845719045681, 0.6549477974515944, 209.5464775076281],
    [5.40266895987223, 0.6748437111130419, 209.54645837410766],
    [5.93592454797767, 0.6944502696114526, 209.54643923893252],
    [6.4986832666748775, 0.7137823011126716, 209.5464201023271],
    [7.091393942308237, 0.7328533701575941, 209.54640096452033],
    [7.714495530830426, 0.7516759233486977, 209.54638182570906],
    [8.362902589291522, 0.7702614142702398, 209.5463626860871],
    [9.010442756551821, 0.7886204111202818, 209.54634354582433],
    [9.653817900540862, 0.8067626898669608, 209.5463244050959],
    [10.29318377392433, 0.8246973152252656, 209.5463052640459],
    [10.928685772528809, 0.8424327113314979, 209.5462861228275],
    [11.56045990779819, 0.8599767236656302, 209.54626698157904],
    [12.188633662809302, 0.8773366735026968, 209.5462478404268],
    [12.813326748632115, 0.8945194059620538, 209.54622869949029],
    [13.434651775012771, 0.9115313325460387, 209.54620955888788],
    [14.0527148470809, 0.928378468919685, 209.54619041872456],
    [14.667616097925809, 0.9450664685622908, 209.5461712791161],
    [15.279450165363095, 0.9616006528304665, 209.54615214014538],
    [15.888306619956744, 0.9779860378836446, 209.5461330019187],
    [16.494270350320917, 0.9942273588675171, 209.54611386451774],
    [17.097421910858294, 1.0103290916839158, 209.54609472803028],
    [17.697837836366574, 1.0262954726377385, 209.5460755925407],
    [18.295590927334914, 1.042130516206454, 209.54605645811773],
    [18.890750509238096, 1.0578380311468378, 209.54603732484748],
    [19.483382668700443, 1.0734216351263122, 209.54601819278727],
    [20.073550469030984, 1.088884768038463, 209.54599906201673],
    [20.661314147315657, 1.1042307041468111, 209.54597993259077],
    [53.38896474111432, 1.8932913045660376, 209.54481718319346],
    [100.0, 2.871588955286716, 209.5429359788321],
    [142.21233355267947, 3.6598615904431204, 209.54109066792404],
    [181.74498695762145, 4.33303753284783, 209.53928262364892],
    [219.379559142843, 4.924275900757143, 209.5375118768831],
    [255.55949550426857, 5.452264905961894, 209.53577795810992],
    [290.56862469201246, 5.929002120237057, 209.53408016967768],
    [324.6031878228979, 6.362852583853973, 209.5324177017366],
    [357.8063946931686, 6.7599912702266085, 209.53078968985596],
    [390.2870215828255, 7.125170758147813, 209.52919524657008],
    [422.13028305191517, 7.462166817890066, 209.52763347977915]]  # type: list[Vector]


def y_to_lstar(y: float, white: VectorLike) -> float:
    """Convert XYZ Y to Lab L*."""

    y = y / white[1]
    fy = alg.nth_root(y, 3) if y > EPSILON else (KAPPA * y + 16) / 116
    return (116.0 * fy) - 16.0


def lstar_to_y(lstar: float, white: VectorLike) -> float:
    """Convert Lab L* to XYZ Y."""

    fy = (lstar + 16) / 116
    y = fy ** 3 if lstar > KE else lstar / KAPPA
    return y * white[1]


def hct_to_xyz(coords: Vector, env: Environment) -> Vector:
    """
    Convert HCT to XYZ.

    Use Newton Raphson method to try and converge as quick as possible or
    converge as close as we can. If we don't converge in about 7 iterations,
    we will instead correct the Y in XYZ and re-calculate the J. This will
    incrementally get our J closer. If we do not converge, we will do a final
    round with Newton Raphson one last time with a more accurate J.

    If, for whatever reason, we cannot achieve the accuracy we seek in the
    allotted iterations, just return the closest we were able to get.
    """

    # Threshold of how close is close enough
    threshold = 2e-8

    h, c, t = coords[:]

    # Shortcut out for black
    if t == 0:
        return [0.0, 0.0, 0.0]

    # Calculate the Y we need to target
    y = lstar_to_y(t, env.ref_white)

    # Try to start with a reasonable initial guess for J
    if c < 142:
        # Calculated by curve fitting J vs T. Works well with colors within a mid-sized gamut, but not ultra wide.
        j = 0.00462403 * t ** 2 + 0.51460278 * t + 2.62845677
    else:
        # For ultra wide gamuts we can get a better J by correcting Y in XYZ and then calculating our J
        xyz = cam16_to_xyz_d65(J=t, C=c, h=h, env=env)
        xyz[1] = y
        j = xyz_d65_to_cam16(xyz, env)[0]

    # Try to find a J such that the returned y matches the returned y of the L*
    attempt = 0
    last = alg.INF
    best = j
    while attempt < 16:
        xyz = cam16_to_xyz_d65(J=j, C=c, h=h, env=env)

        # If we are within range, return XYZ
        # If we are closer than last time, save the values
        delta = abs(xyz[1] - y)
        if delta < last:
            if delta <= threshold:
                return xyz
            best = j
            last = delta

        # Use Newton Raphson method to see if we can quickly converge (or get as close as we can)
        if (attempt < 7 or attempt >= 13) and xyz[1] != 0:
            # ```
            # f(j_root) = (j ** (1 / 2)) * 0.1
            # f(j) = ((f(j_root) * 100) ** 2) / j - 1 = 0
            # f(j_root) = Y = y / 100
            # f(j) = (y ** 2) / j - 1
            # f'(j) = (2 * y) / j
            # ```
            j = j - (xyz[1] - y) * j / (2 * xyz[1])

        # Correct the lightness in XYZ and then re-calculate J
        else:
            xyz[1] = y
            j = xyz_d65_to_cam16(xyz, env)[0]

        attempt += 1

    # We could not acquire the precision we desired, return our closest attempt.
    return cam16_to_xyz_d65(J=best, C=c, h=h, env=env)  # pragma: no cover


def xyz_to_hct(coords: Vector, env: Environment) -> Vector:
    """Convert XYZ to HCT."""

    t = y_to_lstar(coords[1], env.ref_white)
    c, h = xyz_d65_to_cam16(coords, env)[1:3]
    return [h, max(0.0, c), max(0.0, t)]


class Achromatic(_Achromatic):
    """Test HCT achromatic response."""

    # Lightness and chroma (equivalent) index.
    L_IDX = 2
    C_IDX = 1
    H_IDX = 0

    def convert(self, coords: Vector, *, env: Environment, **kwargs: Any) -> Vector:  # type: ignore[override]
        """Convert to the target color space."""

        return xyz_to_hct(lin_srgb_to_xyz(lin_srgb(coords)), env)


class HCT(LChish, Space):
    """HCT class."""

    BASE = "xyz-d65"
    NAME = "hct"
    SERIALIZE = ("--hct",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(
        WHITE,
        200 / math.pi * lstar_to_y(50.0, util.xy_to_xyz(WHITE)),
        lstar_to_y(50.0, util.xy_to_xyz(WHITE)) * 100,
        'average',
        False
    )
    CHANNEL_ALIASES = {
        "lightness": "t",
        "tone": "t",
        "chroma": "c",
        "hue": "h"
    }

    # Achromatic detection
    # Precalculated from:
    # [
    #     (1, 5, 1, 1000.0),
    #     (1, 40, 1, 200.0),
    #     (50, 551, 50, 100.0)
    # ]
    ACHROMATIC = Achromatic(
        ACHROMATIC_RESPONSE,
        0.0097,
        0.0787,
        8.1,
        'catrom',
        env=ENV,
    )

    CHANNELS = (
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE),
        Channel("c", 0.0, 145.0, limit=(0.0, None)),
        Channel("t", 0.0, 100.0, limit=(0.0, None))
    )

    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resolve channels."""

        if index == 0:
            h = coords[0]
            return self.ACHROMATIC.get_ideal_hue(coords[2]) if math.isnan(h) else h

        elif index == 1:
            c = coords[1]
            return self.ACHROMATIC.get_ideal_chroma(coords[0]) if math.isnan(c) else c

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return coords[2] == 0.0 or self.ACHROMATIC.test(coords[2], coords[1], coords[0])

    def names(self) -> tuple[str, ...]:
        """Return LCh-ish names in the order L C h."""

        channels = self.channels
        return channels[2], channels[1], channels[0]

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from CAM16."""

        return hct_to_xyz(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16."""

        return xyz_to_hct(coords, self.ENV)
