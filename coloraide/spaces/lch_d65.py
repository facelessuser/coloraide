"""Lch D65 class."""
from ..cat import WHITES
from ..gamut.bounds import GamutUnbound, FLG_ANGLE
from .lch import Lch


class LchD65(Lch):
    """Lch D65 class."""

    BASE = "lab-d65"
    NAME = "lch-d65"
    SERIALIZE = ("--lch-d65",)
    WHITE = WHITES['2deg']['D65']

    BOUNDS = (
        GamutUnbound(0.0, 100.0),
        GamutUnbound(0.0, 160.0),
        GamutUnbound(0.0, 360.0, FLG_ANGLE)
    )
