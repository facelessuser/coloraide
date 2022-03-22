"""Lab D65 class."""
from ..cat import WHITES
from .lab import Lab


class LabD65(Lab):
    """Lab D65 class."""

    BASE = 'xyz-d65'
    NAME = "lab-d65"
    SERIALIZE = ("--lab-d65",)
    WHITE = WHITES['2deg']['D65']
