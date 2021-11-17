"""A98 RGB color class."""
from ..spaces import RE_DEFAULT_MATCH
from .srgb import SRGB
from .. import util
import re
from ..util import MutableVector
from typing import cast

RGB_TO_XYZ = [
    [0.5766690429101304, 0.18555823790654635, 0.18822864623499475],
    [0.297344975250536, 0.6273635662554663, 0.0752914584939979],
    [0.027031361386412336, 0.07068885253582725, 0.9913375368376391]
]

XYZ_TO_RGB = [
    [2.041587903810747, -0.5650069742788599, -0.34473135077832967],
    [-0.9692436362808794, 1.8759675015077197, 0.04155505740717558],
    [0.013444280632031149, -0.11836239223101835, 1.0151749943912052]
]


def lin_a98rgb_to_xyz(rgb: MutableVector) -> MutableVector:
    """
    Convert an array of linear-light a98-rgb values to CIE XYZ using D50.D65.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    which has greater numerical precision than section 4.3.5.3 of
    https://www.adobe.com/digitalimag/pdfs/AdobeRGB1998.pdf
    """

    return cast(MutableVector, util.dot(RGB_TO_XYZ, rgb))


def xyz_to_lin_a98rgb(xyz: MutableVector) -> MutableVector:
    """Convert XYZ to linear-light a98-rgb."""

    return cast(MutableVector, util.dot(XYZ_TO_RGB, xyz))


def lin_a98rgb(rgb: MutableVector) -> MutableVector:
    """Convert an array of a98-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return [util.npow(val, 563 / 256) for val in rgb]


def gam_a98rgb(rgb: MutableVector) -> MutableVector:
    """Convert an array of linear-light a98-rgb  in the range 0.0-1.0 to gamma corrected form."""

    return [util.npow(val, 256 / 563) for val in rgb]


class A98RGB(SRGB):
    """A98 RGB class."""

    BASE = "xyz"
    NAME = "a98-rgb"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=NAME, channels=3))
    WHITE = "D65"

    @classmethod
    def to_base(cls, coords: MutableVector) -> MutableVector:
        """To XYZ from A98 RGB."""

        return lin_a98rgb_to_xyz(lin_a98rgb(coords))

    @classmethod
    def from_base(cls, coords: MutableVector) -> MutableVector:
        """From XYZ to A98 RGB."""

        return gam_a98rgb(xyz_to_lin_a98rgb(coords))
