"""SRGB color class."""
from ._rgb import RGB
from ._space import RE_DEFAULT_MATCH
import re


class SRGB(RGB):
    """SRGB class."""

    SPACE = "srgb"
    DEF_BG = "color(srgb 0 0 0 / 1)"
    IS_DEFAULT = True
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
