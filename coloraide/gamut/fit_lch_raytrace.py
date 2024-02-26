"""
Gamut mapping by scaling.

This employs a faster approach than bisecting to reduce chroma.
"""
from .fit_oklch_raytrace import OkLChRayTrace


class LChRayTrace(OkLChRayTrace):
    """Apply gamut mapping using ray tracing."""

    NAME = 'lch-raytrace'
    SPACE = "lch-d65"
    MAX_LIGHTNESS = 100
    MIN_LIGHTNESS = 0
