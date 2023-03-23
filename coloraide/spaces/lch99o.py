"""DIN99o LCh class."""
from __future__ import annotations
from ..cat import WHITES
from .lch import LCh
from ..channels import Channel, FLG_ANGLE


class LCh99o(LCh):
    """DIN99o LCh class."""

    BASE = 'din99o'
    NAME = "lch99o"
    SERIALIZE = ("--lch99o",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("c", 0.0, 60.0, limit=(0.0, None)),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )
