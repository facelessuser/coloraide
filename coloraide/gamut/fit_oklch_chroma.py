"""Fit by compressing chroma in Lch."""
from .fit_lch_chroma import LchChroma


class OklchChroma(LchChroma):
    """Lch chroma gamut mapping class."""

    NAME = "oklch-chroma"

    EPSILON = 0.0001
    LIMIT = 0.02
    DE = "ok"
    SPACE = "oklch"
    SPACE_COORDINATE = "{}.chroma".format(SPACE)
