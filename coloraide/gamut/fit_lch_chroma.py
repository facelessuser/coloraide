"""Fit by compressing chroma in OkLCh."""
from __future__ import annotations
from .fit_minde_chroma import MINDEChroma


class LChChroma(MINDEChroma):
    """LCh chroma gamut mapping class."""

    NAME = "lch-chroma"
    JND = 2.0
    DE_OPTIONS = {'method': '2000', 'space': 'lab-d65'}
    PSPACE = "lch-d65"
