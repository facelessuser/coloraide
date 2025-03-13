"""LCh class."""
from __future__ import annotations
from ... import algebra as alg
from ...spaces import Space, LChish
from ...cat import WHITES
from ...channels import Channel, FLG_ANGLE
from ... import util
from ... util import ACHROMATIC_THRESHOLD
import math
from ...types import Vector
from typing import Any


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

    CHANNELS = (
        Channel("l", 0.0, 1.0),
        Channel("c", 0.0, 1.0),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )
    CHANNEL_ALIASES = {
        "lightness": "l",
        "chroma": "c",
        "hue": "h"
    }

    def __init__(self, **kwargs: Any):
        """Initialize."""

        super().__init__(**kwargs)
        order = alg.order(self.channels[self.indexes()[0]].high)
        self.achromatic_threshold = util.ACHROMATIC_THRESHOLD_SM if order == 0 else ACHROMATIC_THRESHOLD

    def normalize(self, coords: Vector) -> Vector:
        """Normalize coordinates."""

        if coords[1] < 0:
            coords[1] *= -1.0
            coords[2] += 180.0
        coords[2] %= 360.0
        return coords

    def is_achromatic(self, coords: Vector) -> bool | None:
        """Check if color is achromatic."""

        # Account for both positive and negative chroma
        return abs(coords[1]) < self.achromatic_threshold

    def to_base(self, coords: Vector) -> Vector:
        """To Lab from LCh."""

        return lch_to_lab(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From Lab to LCh."""

        return lab_to_lch(coords)


class CIELCh(LCh):
    """CIE LCh D50."""

    BASE = "lab"
    NAME = "lch"
    SERIALIZE = ("--lch",)
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("c", 0.0, 150.0),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )
    CHANNEL_ALIASES = {
        "lightness": "l",
        "chroma": "c",
        "hue": "h"
    }
    WHITE = WHITES['2deg']['D50']
