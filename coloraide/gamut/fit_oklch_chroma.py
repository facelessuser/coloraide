"""Fit by compressing chroma in OkLCh."""
from .fit_lch_chroma import LChChroma


class OkLChChroma(LChChroma):
    """OkLCh chroma gamut mapping class."""

    NAME = "oklch-chroma"

    EPSILON = 0.0001
    LIMIT = 0.02
    DE = "ok"
    SPACE = "oklch"
    MAX_LIGHTNESS = 1
