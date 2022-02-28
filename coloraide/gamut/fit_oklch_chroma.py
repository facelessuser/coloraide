"""Fit by compressing chroma in Oklch."""
from .fit_lch_chroma import LchChroma


class OklchChroma(LchChroma):
    """Lch chroma gamut mapping class."""

    NAME = "oklch-chroma"

    EPSILON = 0.001
    LIMIT = 0.02
    DE = "ok"
    SPACE = "oklch"
    MAX_LIGHTNESS = 1
