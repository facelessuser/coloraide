"""LCh D65 class."""
from __future__ import annotations
from ..cat import WHITES
from .lch import CIELCh
from ..channels import Channel, FLG_ANGLE


class LChD65(CIELCh):
    """LCh D65 class."""

    BASE = "lab-d65"
    NAME = "lch-d65"
    SERIALIZE = ("--lch-d65",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("c", 0.0, 160.0),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )
