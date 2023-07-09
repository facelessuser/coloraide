"""
The IPT color space.

https://www.researchgate.net/publication/\
221677980_Development_and_Testing_of_a_Color_Space_IPT_with_Improved_Hue_Uniformity.
"""
from __future__ import annotations
from ..spaces import Space, Labish
from ..channels import Channel, FLG_MIRROR_PERCENT
from .. import algebra as alg
from .achromatic import Achromatic as _Achromatic
from .srgb_linear import lin_srgb_to_xyz
from .srgb import lin_srgb
from ..types import Vector
from typing import Any
import math
from .. import util

XYZ_TO_LMS = [
    [0.4002, 0.7075, -0.0807],
    [-0.2280, 1.1500, 0.0612],
    [0.0, 0.0, 0.9184]
]

LMS_TO_XYZ = [
    [1.8502429449432056, -1.1383016378672328, 0.23843495850870136],
    [0.36683077517134854, 0.6438845448402355, -0.010673443584379992],
    [0.0, 0.0, 1.088850174216028]
]

LMS_P_TO_IPT = [
    [0.4, 0.4, 0.2],
    [4.455, -4.851, 0.396],
    [0.8056, 0.3572, -1.1628]
]

IPT_TO_LMS_P = [
    [1.0000000000000004, 0.0975689305146139, 0.2052264331645916],
    [0.9999999999999997, -0.1138764854731471, 0.13321715836999803],
    [1.0, 0.0326151099170664, -0.6768871830691793]
]

ACHROMATIC_RESPONSE = [
    [0.017066845239980113, 1.321844777655898e-06, 329.76026731764046],
    [0.022993026958471587, 1.7808336678784566e-06, 329.76026731797435],
    [0.02737255832988907, 2.1200328924793134e-06, 329.7602673179663],
    [0.03097697795223092, 2.3991989122003048e-06, 329.7602673180789],
    [0.9999910919149724, 7.745034210925492e-05, 329.7602673179579],
    [5.243613106559707, 0.0004061232467725615, 329.7602673179984]]  # type: list[Vector]


def xyz_to_ipt(xyz: Vector) -> Vector:
    """XYZ to IPT."""

    lms_p = [alg.npow(c, 0.43) for c in alg.dot(XYZ_TO_LMS, xyz, dims=alg.D2_D1)]
    return alg.dot(LMS_P_TO_IPT, lms_p, dims=alg.D2_D1)


def ipt_to_xyz(ipt: Vector) -> Vector:
    """IPT to XYZ."""

    lms = [alg.nth_root(c, 0.43) for c in alg.dot(IPT_TO_LMS_P, ipt, dims=alg.D2_D1)]
    return alg.dot(LMS_TO_XYZ, lms, dims=alg.D2_D1)


class Achromatic(_Achromatic):
    """Test achromatic response."""

    def convert(self, coords: Vector, **kwargs: Any) -> Vector:
        """Convert to the target color space."""

        lab = xyz_to_ipt(lin_srgb_to_xyz(lin_srgb(coords)))
        l = lab[0]
        c, h = alg.rect_to_polar(*lab[1:])
        return [l, c, h]


class IPT(Labish, Space):
    """The IPT class."""

    BASE = "xyz-d65"
    NAME = "ipt"
    SERIALIZE = ("--ipt",)  # type: tuple[str, ...]
    CHANNELS = (
        Channel("i", 0.0, 1.0),
        Channel("p", -1.0, 1.0, flags=FLG_MIRROR_PERCENT),
        Channel("t", -1.0, 1.0, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "intensity": "i",
        "protan": "p",
        "tritan": "t"
    }

    # The D65 white point used in the paper was different than what we use.
    # We use chromaticity points (0.31270, 0.3290) which gives us an XYZ of ~[0.9505, 1.0000, 1.0890]
    # IPT uses XYZ of [0.9504, 1.0, 1.0889] which yields chromaticity points ~(0.3127035830618893, 0.32902313032606195)
    WHITE = tuple(util.xyz_to_xyY([0.9504, 1.0, 1.0889])[:-1])  # type: ignore[assignment]
    # Precalculated from:
    # [
    #     (1, 5, 1, 1000.0),
    #     (100, 101, 1, 100),
    #     (520, 521, 1, 100)
    # ]
    ACHROMATIC = Achromatic(
        ACHROMATIC_RESPONSE,
        1e-5,
        1e-5,
        0.00049,
        'linear',
        mirror=True
    )  # type: _Achromatic

    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resolve channels."""

        if index in (1, 2):
            if not math.isnan(coords[index]):
                return coords[index]

            return self.ACHROMATIC.get_ideal_ab(coords[0])[index - 1]

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        m, h = alg.rect_to_polar(coords[1], coords[2])
        return self.ACHROMATIC.test(coords[0], m, h)

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return ipt_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_to_ipt(coords)
