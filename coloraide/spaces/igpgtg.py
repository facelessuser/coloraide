"""
The IgPgTg color space.

https://www.ingentaconnect.com/content/ist/jpi/2020/00000003/00000002/art00002#
"""
from __future__ import annotations
from .ipt import IPT
from ..channels import Channel, FLG_MIRROR_PERCENT
from ..cat import WHITES
from .. import algebra as alg
from .achromatic import Achromatic as _Achromatic
from .srgb_linear import lin_srgb_to_xyz
from .srgb import lin_srgb
from ..types import Vector, Matrix  # noqa: F401
from typing import Any
import math

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

ACHROMATIC_RESPONSE = [
    [0.01710472400677632, 7.497407788263645e-05, 289.0071727628954],
    [0.022996189520032607, 0.00010079777395973735, 289.00717276289754],
    [0.027343043084773422, 0.00011985106810105086, 289.00717276288543],
    [0.03091688192289772, 0.00013551605464416815, 289.0071727629022],
    [0.9741484960046702, 0.004269924798539192, 289.00717276289504],
    [5.049390603804086, 0.022132681254572965, 289.0071727628912]
]  # type: Matrix


def xyz_to_igpgtg(xyz: Vector) -> Vector:
    """XYZ to IgPgTg."""

    lms_in = alg.matmul(XYZ_TO_LMS, xyz, dims=alg.D2_D1)
    lms = [
        alg.npow(lms_in[0] / 18.36, 0.427),
        alg.npow(lms_in[1] / 21.46, 0.427),
        alg.npow(lms_in[2] / 19435, 0.427)
    ]
    return alg.matmul(LMS_TO_IGPGTG, lms, dims=alg.D2_D1)


def igpgtg_to_xyz(itp: Vector) -> Vector:
    """IgPgTg to XYZ."""

    lms = alg.matmul(IGPGTG_TO_LMS, itp, dims=alg.D2_D1)
    lms_in = [
        alg.nth_root(lms[0], 0.427) * 18.36,
        alg.nth_root(lms[1], 0.427) * 21.46,
        alg.nth_root(lms[2], 0.427) * 19435
    ]
    return alg.matmul(LMS_TO_XYZ, lms_in, dims=alg.D2_D1)


class Achromatic(_Achromatic):
    """Test if color is achromatic."""

    def convert(self, coords: Vector, **kwargs: Any) -> Vector:
        """Convert to the target color space."""

        lab = xyz_to_igpgtg(lin_srgb_to_xyz(lin_srgb(coords)))
        l = lab[0]
        c, h = alg.rect_to_polar(*lab[1:])
        return [l, c, h]


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
        0.03126,
        'linear',
        mirror=True
    )

    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resolve channels."""

        if index in (1, 2):
            if not math.isnan(coords[index]):
                return coords[index]

            return self.ACHROMATIC.get_ideal_ab(coords[0])[index - 1]

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return igpgtg_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_to_igpgtg(coords)
