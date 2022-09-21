"""
The IgPgTg color space.

https://www.ingentaconnect.com/content/ist/jpi/2020/00000003/00000002/art00002#
"""
from __future__ import annotations
from ..spaces import Space, Labish
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
    [0.4343486855574634, -0.20636237011428418, 0.10653033617352772],
    [-0.08785463778363381, 0.20846346647992345, -0.009066845616854866],
    [0.07447971736457795, -0.06330532030466152, 0.44889031421761344]
]

LMS_TO_IGPGTG = [
    [0.117, 1.464, 0.13],
    [8.285, -8.361, 21.4],
    [-1.208, 2.412, -36.53]
]

IGPGTG_TO_LMS = [
    [0.5818464618992484, 0.1233185479390782, 0.07431308420320765],
    [0.6345481937914158, -0.009437923746683553, -0.003270744675229782],
    [0.022656986516578225, -0.0047011518748263665, -0.030048158824914562]
]


def xyz_to_igpgtg(xyz: Vector) -> Vector:
    """XYZ to IgPgTg."""

    lms_in = alg.dot(XYZ_TO_LMS, xyz, dims=alg.D2_D1)
    lms = [
        alg.npow(lms_in[0] / 18.36, 0.427),
        alg.npow(lms_in[1] / 21.46, 0.427),
        alg.npow(lms_in[2] / 19435, 0.427)
    ]
    return alg.dot(LMS_TO_IGPGTG, lms, dims=alg.D2_D1)


def igpgtg_to_xyz(itp: Vector) -> Vector:
    """IgPgTg to XYZ."""

    lms = alg.dot(IGPGTG_TO_LMS, itp, dims=alg.D2_D1)
    lms_in = [
        alg.nth_root(lms[0], 0.427) * 18.36,
        alg.nth_root(lms[1], 0.427) * 21.46,
        alg.nth_root(lms[2], 0.427) * 19435
    ]
    return alg.dot(LMS_TO_XYZ, lms_in, dims=alg.D2_D1)


class IgPgTg(Labish, Space):
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
        "intensity": "i",
        "protan": "cp",
        "tritan": "ct"
    }
    WHITE = WHITES['2deg']['D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return igpgtg_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_to_igpgtg(coords)
