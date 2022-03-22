"""Lab D65 class."""
from ..cat import WHITES
from ..gamut.bounds import GamutUnbound
from .lab import Lab


class LabD65(Lab):
    """Lab D65 class."""

    BASE = 'xyz-d65'
    NAME = "lab-d65"
    SERIALIZE = ("--lab-d65",)
    WHITE = WHITES['2deg']['D65']

    BOUNDS = (
        GamutUnbound(0.0, 100.0),
        GamutUnbound(-130, 130),
        GamutUnbound(-130, 130)
    )
