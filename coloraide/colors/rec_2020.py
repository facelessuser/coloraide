"""Rec 2020 color class."""
from ._rgb import RGB


class Rec_2020(RGB):
    """Rec 2020 class."""

    SPACE = "rec-2020"
    DEF_BG = "color(rec-2020 0 0 0 / 1)"

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
