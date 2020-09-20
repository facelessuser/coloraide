"""Pro Photo RGB color class."""
from ._rgb import _RGBColor


class ProPhoto_RGB(_RGBColor):
    """Pro Photo RGB class."""

    SPACE = "prophoto-rgb"
    DEF_BG = "color(prophoto-rgb 0 0 0 / 1)"

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
