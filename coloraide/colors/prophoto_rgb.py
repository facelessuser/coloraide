"""Pro Photo RGB color class."""
from ._rgb import RGB
from ._space import RE_DEFAULT_MATCH
from . import _convert as convert
import re


class ProPhoto_RGB(RGB):
    """Pro Photo RGB class."""

    SPACE = "prophoto-rgb"
    DEF_BG = "color(prophoto-rgb 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

    @classmethod
    def _to_xyz(cls, rgb):
        """To XYZ."""

        return convert.prophoto_rgb_to_xyz(rgb)

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return convert.xyz_to_prophoto_rgb(xyz)
