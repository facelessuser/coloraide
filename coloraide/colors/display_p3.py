"""Display-p3 color class."""
from ._rgb import RGB
from ._space import RE_DEFAULT_MATCH
from . import _convert as convert
import re


class Display_P3(RGB):
    """Display-p3 class."""

    SPACE = "display-p3"
    DEF_BG = "color(display-p3 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

    @classmethod
    def _to_xyz(cls, rgb):
        """To XYZ."""

        return convert.display_p3_to_xyz(rgb)

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return convert.xyz_to_display_p3(xyz)
