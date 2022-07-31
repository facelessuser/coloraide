"""ColorAide Library."""
from .__meta__ import __version_info__, __version__  # noqa: F401
from .color import Color, ColorMatch
from .interpolate import stop, hint
from .algebra import NaN
from .easing import cubic_bezier, linear, ease, ease_in, ease_out, ease_in_out

__all__ = (
    "Color", "ColorMatch", "NaN", "stop", "hint", "cubic_bezier",
    "linear", "ease", "ease_in", "ease_out", "ease_in_out"
)
