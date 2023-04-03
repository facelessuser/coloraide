"""LCh class."""
from __future__ import annotations
from ...spaces import Space, LChish
from ...cat import WHITES
from ...channels import Channel, FLG_ANGLE, FLG_OPT_PERCENT
from ... import util
import math
from ...types import Vector

ACHROMATIC_THRESHOLD = 1e-4


def lab_to_lch(lab: Vector) -> Vector:
    """Lab to LCh."""

    l, a, b = lab

    c = math.sqrt(a ** 2 + b ** 2)
    h = math.degrees(math.atan2(b, a))

    return [l, c, util.constrain_hue(h)]


def lch_to_lab(lch: Vector) -> Vector:
    """LCh to Lab."""

    l, c, h = lch

    return [
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    ]


class LCh(LChish, Space):
    """LCh class."""

    BASE = "lab"
    NAME = "lch"
    SERIALIZE = ("--lch",)
    CHANNELS = (
        Channel("l", 0.0, 100.0, flags=FLG_OPT_PERCENT),
        Channel("c", 0.0, 150.0, limit=(0.0, None), flags=FLG_OPT_PERCENT),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )
    CHANNEL_ALIASES = {
        "lightness": "l",
        "chroma": "c",
        "hue": "h"
    }
    WHITE = WHITES['2deg']['D50']

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return coords[1] < ACHROMATIC_THRESHOLD

    def to_base(self, coords: Vector) -> Vector:
        """To Lab from LCh."""

        return lch_to_lab(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From Lab to LCh."""

        return lab_to_lch(coords)
