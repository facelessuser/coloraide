"""Colors."""
from .hsv import _HSV
from .srgb import _SRGB
from .hsl import _HSL
from .hwb import _HWB
from .lab import _LAB
from .lch import _LCH
from ..matcher import color_match, color_fullmatch

__all__ = ("HSV", "SRGB", "HSL", "HWB", "LAB", "LCH")

SPACES = frozenset({"srgb", "hsl", "hsv", "hwb", "lch", "lab"})

CS_MAP = {}


class HSV(_HSV):
    """HSV color class."""

    spaces = CS_MAP


class SRGB(_SRGB):
    """RGB color class."""

    spaces = CS_MAP


class HSL(_HSL):
    """HSL color class."""

    spaces = CS_MAP


class HWB(_HWB):
    """HWB color class."""

    spaces = CS_MAP


class LAB(_LAB):
    """HWB color class."""

    spaces = CS_MAP


class LCH(_LCH):
    """HWB color class."""

    spaces = CS_MAP


SUPPORTED = (HSV, HSL, HWB, LAB, LCH, SRGB)
for obj in SUPPORTED:
    CS_MAP[obj.space()] = obj


def colorgen(string, spaces=SPACES):
    """Match a color and return a match object."""

    return color_fullmatch(string, SUPPORTED, SPACES)


def colorgen_match(string, start=0, fullmatch=False, spaces=SPACES):
    """Match a color and return a match object."""

    return color_match(string, start, fullmatch, SUPPORTED, SPACES)
