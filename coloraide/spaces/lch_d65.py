"""Lch D65 class."""
from ..cat import WHITES
from .lch import Lch


class LchD65(Lch):
    """Lch D65 class."""

    BASE = "lab-d65"
    NAME = "lch-d65"
    SERIALIZE = ("--lch-d65",)
    WHITE = WHITES['2deg']['D65']
