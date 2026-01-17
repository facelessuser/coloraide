"""
Simple Color Appearance Model (sUCS).

https://opg.optica.org/oe/fulltext.cfm?uri=oe-32-3-3100&id=545619
"""
from __future__ import annotations
import math
from .. import algebra as alg
from .lch import LCh
from ..channels import Channel, FLG_ANGLE
from .ipt import XYZ_TO_LMS, LMS_TO_XYZ
from ..cat import WHITES
from ..types import Vector

# Iab transformation matrices
TO_IAB = [
    alg.divide([200.0, 100.0, 5.0], 3.05, dims=alg.D1_SC),
    [430.0, -470.0, 40.0],
    [49.0, 49.0, -98.0]
]
FROM_IAB = alg.inv(TO_IAB)


def sucs_to_xyz(ich: Vector) -> Vector:
    """From sUCS to XYZ."""

    i, c, h = ich
    c = (math.exp(0.0252 * c) - 1) / 0.0447
    r = math.radians(h)
    a, b = c * math.cos(r), c * math.sin(r)
    lms = [alg.nth_root(x, 0.43) for x in alg.matmul_x3(FROM_IAB, [i, a, b], dims=alg.D2_D1)]
    return alg.matmul_x3(LMS_TO_XYZ, lms, dims=alg.D2_D1)


def xyz_to_sucs(xyz: Vector) -> Vector:
    """From XYZ to sUCS."""

    lms_p = [alg.spow(i, 0.43) for i in alg.matmul_x3(XYZ_TO_LMS, xyz, dims=alg.D2_D1)]
    i, a, b = alg.matmul_x3(TO_IAB, lms_p, dims=alg.D2_D1)
    c = (1 / 0.0252) * math.log(1 + 0.0447 * math.sqrt(a ** 2 + b ** 2))
    h = math.atan2(b, a) % math.tau
    return [i, c, math.degrees(h)]


class sUCS(LCh):
    """sUCS class."""

    BASE = "xyz-d65"
    NAME = "sucs"
    SERIALIZE = ("--sucs",)
    CHANNEL_ALIASES = {
        "intensity": "i",
        "chroma": 'c',
        "hue": 'h'
    }
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("i", 0.0, 100),
        Channel("c", 0, 65.0),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "i"

    def normalize(self, coords: Vector) -> Vector:
        """Normalize."""

        if coords[1] < 0.0:
            return self.from_base(self.to_base(coords))
        coords[2] %= 360.0
        return coords

    def to_base(self, coords: Vector) -> Vector:
        """From sCAM JMh to XYZ."""

        return sucs_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to sCAM JMh."""

        return xyz_to_sucs(coords)
