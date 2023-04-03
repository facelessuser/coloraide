"""LChuv class."""
from __future__ import annotations
from ..spaces import Space
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .lch import LCh, ACHROMATIC_THRESHOLD
from ..types import Vector


class LChuv(LCh, Space):
    """LChuv class."""

    BASE = "luv"
    NAME = "lchuv"
    SERIALIZE = ("--lchuv",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("c", 0.0, 220.0, limit=(0.0, None)),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return coords[0] == 0.0 or coords[1] < ACHROMATIC_THRESHOLD
