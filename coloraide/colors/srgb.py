"""SRGB color class."""
from ._rgb import RGB
from ._space import RE_DEFAULT_MATCH
from . import _convert as convert
import re


class SRGB(RGB):
    """SRGB class."""

    SPACE = "srgb"
    DEF_BG = "color(srgb 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

    @classmethod
    def _to_xyz(cls, rgb):
        """SRGB to XYZ."""

        return convert.srgb_to_xyz(rgb)

    @classmethod
    def _from_xyz(cls, xyz):
        """XYZ to SRGB."""

        return convert.xyz_to_srgb(xyz)
