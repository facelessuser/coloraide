"""Colors."""
from .srgb import SRGB
from .hsl import HSL
from .hwb import HWB
from .lab import LAB
from .lch import LCH
from ...colors import HSV
from ...colors import Display_P3
from ...colors import A98_RGB
from ...colors import ProPhoto_RGB
from ...colors import Rec_2020
from ...colors import Color as GenericColor


class Color(GenericColor):
    """Color wrapper class."""

    SUPPORTED = (
        HSL, HWB, LAB, LCH, SRGB, HSV,
        Display_P3, A98_RGB, ProPhoto_RGB, Rec_2020
    )
    CS_MAP = {obj.space(): obj for obj in SUPPORTED}
