"""
CAM 16 UCS.

https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067
https://doi.org/10.1002/col.22131
"""
from __future__ import annotations
import math
from . cam16 import CAM16
from ..types import Vector
from ..channels import Channel, FLG_MIRROR_PERCENT

COEFFICENTS = {
    'lcd': (0.77, 0.007, 0.0053),
    'scd': (1.24, 0.007, 0.0363),
    'ucs': (1.00, 0.007, 0.0228)
}


def cam16_to_cam16_ucs(jab: Vector, model: str) -> Vector:
    """
    CAM16 (Jab) to CAM16 UCS (Jab).

    We can actually go between simply by removing the old colorfulness multiplier
    and then adding the new adjusted multiplier. Then we can just adjust lightness.
    """

    J, a, b = jab
    M = math.sqrt(a ** 2 + b ** 2)

    c1, c2 = COEFFICENTS[model][1:]

    if M != 0:
        a /= M
        b /= M
        M = math.log(1 + c2 * M) / c2
        a *= M
        b *= M

    return [
        (1 + 100 * c1) * J / (1 + c1 * J),
        a,
        b
    ]


def cam16_ucs_to_cam16(ucs: Vector, model: str) -> Vector:
    """
    CAM16 UCS (Jab) to CAM16 (Jab).

    We can actually go between simply by removing the old colorfulness multiplier
    and then adding the new adjusted multiplier. Then we can just adjust lightness.
    """

    J, a, b = ucs
    M = math.sqrt(a ** 2 + b ** 2)

    c1, c2 = COEFFICENTS[model][1:]

    if M != 0:
        a /= M
        b /= M
        M = (math.exp(M * c2) - 1) / c2
        a *= M
        b *= M

    return [
        J / (1 - c1 * (J - 100)),
        a,
        b
    ]


class CAM16UCS(CAM16):
    """CAM16 UCS (Jab) class."""

    BASE = "cam16"
    NAME = "cam16-ucs"
    SERIALIZE = ("--cam16-ucs",)
    MODEL = 'ucs'
    CHANNELS = (
        Channel("j", 0.0, 100.0, limit=(0.0, None)),
        Channel("a", -50.0, 50.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -50.0, 50.0, flags=FLG_MIRROR_PERCENT)
    )

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from CAM16."""

        return cam16_ucs_to_cam16(coords, self.MODEL)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16."""

        return cam16_to_cam16_ucs(coords, self.MODEL)


class CAM16LCD(CAM16UCS):
    """CAM16 LCD (Jab) class."""

    NAME = "cam16-lcd"
    SERIALIZE = ("--cam16-lcd",)
    ENV = ENV = CAM16.ENV
    MODEL = 'lcd'
    CHANNELS = (
        Channel("j", 0.0, 100.0, limit=(0.0, None)),
        Channel("a", -70.0, 70.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -70.0, 70.0, flags=FLG_MIRROR_PERCENT)
    )


class CAM16SCD(CAM16UCS):
    """CAM16 SCD (Jab) class."""

    NAME = "cam16-scd"
    SERIALIZE = ("--cam16-scd",)
    ENV = ENV = CAM16.ENV
    MODEL = 'scd'
    CHANNELS = (
        Channel("j", 0.0, 100.0, limit=(0.0, None)),
        Channel("a", -40.0, 40.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -40.0, 40.0, flags=FLG_MIRROR_PERCENT)
    )
