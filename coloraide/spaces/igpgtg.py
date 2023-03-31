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
from ..types import Vector
from typing import Any
import math

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

ACHROMATIC_RESPONSE = [
    [0.01710472400677632, 7.497407788263028e-05, 289.00717276288583],
    [0.022996189520032607, 0.00010079777395972956, 289.0071727628907],
    [0.027343043084773415, 0.00011985106810106645, 289.0071727628969],
    [0.030916881922897717, 0.00013551605464415584, 289.00717276289157],
    [0.9741484960046701, 0.004269924798539691, 289.0071727629053],
    [5.049390603804086, 0.022132681254573808, 289.00717276289043]]  # type: list[Vector]


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
