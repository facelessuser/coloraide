"""
The IgPgTg color space.

https://www.ingentaconnect.com/content/ist/jpi/2020/00000003/00000002/art00002#
"""
from __future__ import annotations
from .ipt import IPT
from ..channels import Channel, FLG_MIRROR_PERCENT
from ..cat import WHITES
from .. import algebra as alg
from ..types import Vector

XYZ_TO_LMS = [
    [2.968, 2.741, -0.649],
    [1.237, 5.969, -0.173],
    [-0.318, 0.387, 2.311]
]

LMS_TO_XYZ = [
    [0.4343486855574635, -0.20636237011428415, 0.10653033617352774],
    [-0.08785463778363382, 0.20846346647992342, -0.009066845616854866],
    [0.07447971736457797, -0.06330532030466152, 0.44889031421761344]
]

LMS_TO_IGPGTG = [
    [0.117, 1.464, 0.13],
    [8.285, -8.361, 21.4],
    [-1.208, 2.412, -36.53]
]

IGPGTG_TO_LMS = [
    [0.5818464618992462, 0.12331854793907822, 0.07431308420320765],
    [0.634548193791416, -0.009437923746683556, -0.0032707446752297835],
    [0.02265698651657832, -0.004701151874826367, -0.030048158824914562]
]


def xyz_to_igpgtg(xyz: Vector) -> Vector:
    """XYZ to IgPgTg."""

    lms_in = alg.matmul_x3(XYZ_TO_LMS, xyz, dims=alg.D2_D1)
    lms = [
        alg.spow(lms_in[0] / 18.36, 0.427),
        alg.spow(lms_in[1] / 21.46, 0.427),
        alg.spow(lms_in[2] / 19435, 0.427)
    ]
    return alg.matmul_x3(LMS_TO_IGPGTG, lms, dims=alg.D2_D1)


def igpgtg_to_xyz(itp: Vector) -> Vector:
    """IgPgTg to XYZ."""

    lms = alg.matmul_x3(IGPGTG_TO_LMS, itp, dims=alg.D2_D1)
    lms_in = [
        alg.nth_root(lms[0], 0.427) * 18.36,
        alg.nth_root(lms[1], 0.427) * 21.46,
        alg.nth_root(lms[2], 0.427) * 19435
    ]
    return alg.matmul_x3(LMS_TO_XYZ, lms_in, dims=alg.D2_D1)


class IgPgTg(IPT):
    """The IgPgTg class."""

    BASE = "xyz-d65"
    NAME = "igpgtg"
    SERIALIZE = ("--igpgtg",)  # type: tuple[str, ...]
    CHANNELS = (
        Channel("ig", 0.0, 1.0),
        Channel("pg", -1.0, 1.0, flags=FLG_MIRROR_PERCENT),
        Channel("tg", -1.0, 1.0, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "intensity": "ig",
        "protan": "pg",
        "tritan": "tg"
    }
    WHITE = WHITES['2deg']['D65']

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "ig"

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return igpgtg_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_to_igpgtg(coords)
