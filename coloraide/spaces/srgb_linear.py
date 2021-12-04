"""SRGB Linear color class."""
from ..spaces import RE_DEFAULT_MATCH
from .srgb import SRGB
import re
from ..util import MutableVector
from typing import cast
from ..import util


RGB_TO_XYZ = [
    [0.4123907992659593, 0.357584339383878, 0.18048078840183432],
    [0.21263900587151024, 0.715168678767756, 0.07219231536073373],
    [0.01933081871559182, 0.11919477979462598, 0.9505321522496608]
]

XYZ_TO_RGB = [
    [3.2409699419045226, -1.537383177570094, -0.49861076029300355],
    [-0.9692436362808796, 1.8759675015077202, 0.04155505740717562],
    [0.055630079696993635, -0.2039769588889765, 1.0569715142428784]
]


def lin_srgb_to_xyz(rgb: MutableVector) -> MutableVector:
    """
    Convert an array of linear-light sRGB values to CIE XYZ using sRGB's own white.

    D65 (no chromatic adaptation)
    """

    return cast(MutableVector, util.dot(RGB_TO_XYZ, rgb))


def xyz_to_lin_srgb(xyz: MutableVector) -> MutableVector:
    """Convert XYZ to linear-light sRGB."""

    return cast(MutableVector, util.dot(XYZ_TO_RGB, xyz))


class SRGBLinear(SRGB):
    """SRGB linear."""

    BASE = 'xyz-d65'
    NAME = "srgb-linear"
    SERIALIZE = ("srgb-linear",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    @classmethod
    def to_base(cls, coords: MutableVector) -> MutableVector:
        """To XYZ from SRGB Linear."""

        return lin_srgb_to_xyz(coords)

    @classmethod
    def from_base(cls, coords: MutableVector) -> MutableVector:
        """From XYZ to SRGB Linear."""

        return xyz_to_lin_srgb(coords)
