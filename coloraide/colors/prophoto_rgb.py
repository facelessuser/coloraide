"""Pro Photo RGB color class."""
import re
from ._rgb import _RGBColor
from ..util import parse


class _ProPhoto_RGB(_RGBColor):
    """Pro Photo RGB class."""

    SPACE = "prophoto-rgb"
    DEF_BG = "color(prophoto-rgb 0 0 0 / 1)"
    _MATCH = re.compile(
        r"(?xi)color\(\s*prophoto-rgb\s+((?:{float}{sep}){{2}}{float}(?:{asep}(?:{percent}|{float}))?)\s*\)".format(
            **parse.COLOR_PARTS
        )
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
