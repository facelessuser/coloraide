"""Colors."""
from .srgb import SRGB
from .hsl import HSL
from .hwb import HWB
from .lab import LAB
from .lch import LCH
from ...colors import SRGBLinear
from ...colors import HSV
from ...colors import DisplayP3
from ...colors import A98RGB
from ...colors import ProPhotoRGB
from ...colors import Rec2020
from ...colors import XYZ
from ...colors import XYZD65
from ...colors import Color as GenericColor

SUPPORTED = (
    HSL, HWB, LAB, LCH, SRGB, SRGBLinear, HSV,
    DisplayP3, A98RGB, ProPhotoRGB, Rec2020, XYZ, XYZD65
)


class Color(GenericColor):
    """Color wrapper class."""

    CS_MAP = {obj.space(): obj for obj in SUPPORTED}
