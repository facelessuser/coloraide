"""Display-p3 color class."""
from ._rgb import RGB
from ._space import RE_DEFAULT_MATCH
import re


class Display_P3(RGB):
    """Display-p3 class."""

    SPACE = "display-p3"
    DEF_BG = "color(display-p3 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
