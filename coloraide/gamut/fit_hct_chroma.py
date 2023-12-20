"""HCT gamut mapping."""
from __future__ import annotations
from ..gamut.fit_lch_chroma import LChChroma


class HCTChroma(LChChroma):
    """HCT chroma gamut mapping class."""

    NAME = "hct-chroma"

    EPSILON = 0.01
    LIMIT = 2.0
    DE = "hct"
    DE_OPTIONS = {}
    SPACE = "hct"
    MIN_LIGHTNESS = 0
    MAX_LIGHTNESS = 100
    MIN_CONVERGENCE = 0.0001
