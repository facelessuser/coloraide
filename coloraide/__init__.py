"""ColorAide Library."""
from .__meta__ import __version_info__, __version__  # noqa: F401
from .color import Color, ColorAll, ColorMatch
from .interpolate import stop, hint
from .algebra import NaN

__all__ = ("Color", "ColorAll", "ColorMatch", "NaN", "stop", "hint")
