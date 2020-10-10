"""ColorAide Library."""
from .__meta__ import __version_info__, __version__  # noqa: F401
from .css import Color
from .colors import ColorMatch

__all__ = ("Color", "ColorMatch")
