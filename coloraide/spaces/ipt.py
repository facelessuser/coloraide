"""
The IPT color space.

https://www.researchgate.net/publication/\
221677980_Development_and_Testing_of_a_Color_Space_IPT_with_Improved_Hue_Uniformity.
"""
from __future__ import annotations
from .lab import Lab
from ..channels import Channel, FLG_MIRROR_PERCENT
from .. import algebra as alg
from .. import util
from ..types import Vector

# IPT matrices for LMS conversion with better accuracy for 64 bit doubles
XYZ_TO_LMS = [
    [0.40021823485770675, 0.7075142362766385, -0.08070681117219487],
    [-0.2279857874604858, 1.1499981023974668, 0.061235733313416064],
    [0.0, 0.0, 0.918357975939021]
]

LMS_TO_XYZ = [
    [1.8502, -1.1383, 0.2385],
    [0.3668, 0.6439, -0.0107],
    [0.0, 0.0, 1.0889]
]

LMS_P_TO_IPT = [
    [0.4000, 0.4000, 0.2000],
    [4.4550, -4.8510, 0.3960],
    [0.8056, 0.3572, -1.1628]
]

IPT_TO_LMS_P = [
    [1.0, 0.0975689305146139, 0.20522643316459155],
    [1.0, -0.11387648547314713, 0.133217158369998],
    [1.0, 0.03261510991706641, -0.6768871830691794]
]


def xyz_to_ipt(xyz: Vector) -> Vector:
    """XYZ to IPT."""

    lms_p = [alg.spow(c, 0.43) for c in alg.matmul_x3(XYZ_TO_LMS, xyz, dims=alg.D2_D1)]
    return alg.matmul_x3(LMS_P_TO_IPT, lms_p, dims=alg.D2_D1)


def ipt_to_xyz(ipt: Vector) -> Vector:
    """IPT to XYZ."""

    lms = [alg.nth_root(c, 0.43) for c in alg.matmul_x3(IPT_TO_LMS_P, ipt, dims=alg.D2_D1)]
    return alg.matmul_x3(LMS_TO_XYZ, lms, dims=alg.D2_D1)


class IPT(Lab):
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

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "i"

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return ipt_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_to_ipt(coords)
