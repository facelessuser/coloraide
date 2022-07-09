"""ColorAide Library."""
from .__meta__ import __version_info__, __version__  # noqa: F401
from .color import Color, ColorMatch
from .interpolate import stop, hint
from .algebra import NaN

__all__ = ("Color", "ColorMatch", "NaN", "stop", "hint")
