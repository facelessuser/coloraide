"""SRGB color class."""
import re
from ._rgb import _RGBColor
from ..util import parse
from ..util import convert


class _SRGB(_RGBColor):
    """SRGB class."""

    SPACE = "srgb"
    DEF_BG = "color(srgb 0 0 0 / 1)"
    _MATCH = re.compile(
        r"(?xi)color\(\s*srgb\s+((?:{float}{sep}){{2}}{float}(?:{asep}(?:{percent}|{float}))?)\s*\)".format(
            **parse.COLOR_PARTS
        )
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
