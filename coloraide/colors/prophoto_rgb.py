"""Pro Photo RGB color class."""
from ._rgb import RGB
from ._space import RE_DEFAULT_MATCH
import re


class ProPhoto_RGB(RGB):
    """Pro Photo RGB class."""

    SPACE = "prophoto-rgb"
    DEF_BG = "color(prophoto-rgb 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
