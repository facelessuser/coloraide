"""A98 RGB color class."""
from ._rgb import RGB
from ._space import RE_DEFAULT_MATCH
import re


class A98_RGB(RGB):
    """A98 RGB class."""

    SPACE = "a98-rgb"
    DEF_BG = "color(a98-rgb 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
