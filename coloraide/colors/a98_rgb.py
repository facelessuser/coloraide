"""A98 RGB color class."""
import re
from ._rgb import _RGBColor
from ..util import parse


class _A98_RGB(_RGBColor):
    """A98 RGB class."""

    SPACE = "a98-rgb"
    DEF_BG = "color(a98-rgb 0 0 0 / 1)"
    _MATCH = re.compile(
        r"(?xi)color\(\s*a98-rgb\s+((?:{float}{sep}){{2}}{float}(?:{asep}(?:{percent}|{float}))?)\s*\)".format(
            **parse.COLOR_PARTS
        )
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
