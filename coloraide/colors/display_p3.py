"""Display-p3 color class."""
import re
from ._rgb import _RGBColor
from ..util import parse


class _Display_P3(_RGBColor):
    """Display-p3 class."""

    SPACE = "display-p3"
    DEF_BG = "color(display-p3 0 0 0 / 1)"
    _MATCH = re.compile(
        r"(?xi)color\(\s*display-p3\s+((?:{float}{sep}){{2}}{float}(?:{asep}(?:{percent}|{float}))?)\s*\)".format(
            **parse.COLOR_PARTS
        )
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
