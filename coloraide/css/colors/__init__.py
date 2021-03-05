"""Colors."""
from .srgb import SRGB
from .hsl import HSL
from .hwb import HWB
from .lab import LAB
from .lch import LCH
from ...colors import SRGB_Linear
from ...colors import HSV
from ...colors import Display_P3
from ...colors import A98_RGB
from ...colors import ProPhoto_RGB
from ...colors import Rec2020
from ...colors import XYZ
from ...colors import Color as GenericColor

SUPPORTED = (
    HSL, HWB, LAB, LCH, SRGB, SRGB_Linear, HSV,
    Display_P3, A98_RGB, ProPhoto_RGB, Rec2020, XYZ
)


class Color(GenericColor):
    """Color wrapper class."""

    CS_MAP = {obj.space(): obj for obj in SUPPORTED}
