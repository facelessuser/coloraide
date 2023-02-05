"""HCT gamut mapping."""
from __future__ import annotations
from ..gamut.fit_lch_chroma import LChChroma


class HCTChroma(LChChroma):
    """HCT chroma gamut mapping class."""

    NAME = "hct-chroma"

    EPSILON = 0.001
    LIMIT = 0.02
    DE = "hct"
    SPACE = "hct"
    MIN_LIGHTNESS = 0
    MAX_LIGHTNESS = 100
    MIN_CONVERGENCE = 0.0001
