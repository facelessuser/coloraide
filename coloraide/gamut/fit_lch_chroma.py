"""Fit by compressing chroma in Lch."""
from .fit_oklch_chroma import OklchChroma


class LchChroma(OklchChroma):
    """Lch chroma gamut mapping class."""

    NAME = "lch-chroma"

    EPSILON = 0.01
    LIMIT = 2.0
    DE = "2000"
    SPACE = "lch"
    SPACE_COORDINATE = "{}.chroma".format(SPACE)
