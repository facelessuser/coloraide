"""Fit by compressing chroma in OkLCh."""
from __future__ import annotations
from .fit_minde_chroma import MINDEChroma


class OkLChChroma(MINDEChroma):
    """OkLCh chroma gamut mapping class."""

    NAME = "oklch-chroma"
