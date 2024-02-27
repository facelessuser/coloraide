"""Gamut map using ray tracing."""
from .fit_raytrace import RayTrace


class LChRayTrace(RayTrace):
    """Apply gamut mapping using ray tracing."""

    NAME = 'lch-raytrace'
    SPACE = "lch-d65"
