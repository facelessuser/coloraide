"""Lab D65 class."""
from __future__ import annotations
from ..cat import WHITES
from .lab import Lab
from ..channels import Channel, FLG_MIRROR_PERCENT


class LabD65(Lab):
    """Lab D65 class."""

    BASE = 'xyz-d65'
    NAME = "lab-d65"
    SERIALIZE = ("--lab-d65",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("a", -130.0, 130.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -130.0, 130.0, flags=FLG_MIRROR_PERCENT)
    )
