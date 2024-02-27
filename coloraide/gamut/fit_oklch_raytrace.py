"""Gamut map using ray tracing."""
from .fit_raytrace import RayTrace


class OkLChRayTrace(RayTrace):
    """Apply gamut mapping using ray tracing."""

    NAME = 'oklch-raytrace'
    SPACE = "oklch"
