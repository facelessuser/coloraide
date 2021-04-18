"""CSS Color object."""
from .spaces.srgb import SRGB
from .spaces.hsl import HSL
from .spaces.hwb import HWB
from .spaces.lab import Lab
from .spaces.lch import Lch
from ..color import Color as GenericColor

CSS_OVERRIDES = (HSL, HWB, Lab, Lch, SRGB)


class Color(GenericColor):
    """Color wrapper class."""

    CS_MAP = {key: value for key, value in GenericColor.CS_MAP.items()}
    for color in CSS_OVERRIDES:
        CS_MAP[color.space()] = color
