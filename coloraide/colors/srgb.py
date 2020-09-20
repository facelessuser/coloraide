"""SRGB color class."""
from ._rgb import RGB


class SRGB(RGB):
    """SRGB class."""

    SPACE = "srgb"
    DEF_BG = "color(srgb 0 0 0 / 1)"
    IS_DEFAULT = True

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
