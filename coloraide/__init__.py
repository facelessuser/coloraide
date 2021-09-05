"""ColorAide Library."""
from .__meta__ import __version_info__, __version__  # noqa: F401
from .color import Color
from .color.match import ColorMatch
from .color.interpolate import Piecewise, Lerp
from .util import NaN

__all__ = ("Color", "ColorMatch", "NaN", "Piecewise", "Lerp")
