"""Display-p3 color class."""
from ._rgb import _RGBColor


class _Display_P3(_RGBColor):
    """Display-p3 class."""

    SPACE = "display-p3"
    DEF_BG = "color(display-p3 0 0 0 / 1)"

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
