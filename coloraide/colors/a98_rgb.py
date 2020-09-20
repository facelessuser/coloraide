"""A98 RGB color class."""
from ._rgb import RGB


class A98_RGB(RGB):
    """A98 RGB class."""

    SPACE = "a98-rgb"
    DEF_BG = "color(a98-rgb 0 0 0 / 1)"

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
