"""ColorAide Library."""
from .__meta__ import __version_info__, __version__  # noqa: F401
from .color import Color, ColorLegacy, ColorMatch
from .interpolate import Piecewise, Lerp
from .algebra import NaN

__all__ = ("Color", "ColorLegacy", "ColorMatch", "NaN", "Piecewise", "Lerp")
