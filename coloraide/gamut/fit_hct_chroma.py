"""HCT gamut mapping."""
from __future__ import annotations
from ..gamut.fit_minde_chroma import MINDEChroma


class HCTChroma(MINDEChroma):
    """HCT chroma gamut mapping class."""

    NAME = "hct-chroma"
    JND = 2.0
    DE_OPTIONS = {"method": "hct"}
    PSPACE = "hct"
