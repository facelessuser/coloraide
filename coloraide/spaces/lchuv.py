"""LChuv class."""
from __future__ import annotations
from .lch import LCh
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from ..types import Vector


class LChuv(LCh):
    """LChuv class."""

    BASE = "luv"
    NAME = "lchuv"
    SERIALIZE = ("--lchuv",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("c", 0.0, 220.0),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return coords[0] == 0.0 or coords[1] < self.achromatic_threshold
