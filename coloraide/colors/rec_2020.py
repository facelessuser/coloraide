"""Rec 2020 color class."""
import re
from ._rgb import _RGBColor
from ..util import parse


class _Rec_2020(_RGBColor):
    """Rec 2020 class."""

    SPACE = "rec-2020"
    DEF_BG = "color(rec-2020 0 0 0 / 1)"
    _MATCH = re.compile(
        r"(?xi)color\(\s*rec2020\s+((?:{float}{sep}){{2}}{float}(?:{asep}{float})?)\s*\)".format(**parse.COLOR_PARTS)
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
