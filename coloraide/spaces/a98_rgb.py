"""A98 RGB color class."""
from ..spaces import RE_DEFAULT_MATCH
from .srgb.base import SRGB
from .xyz import XYZ
from .. import util
import re
from ..util import Vector, MutableVector
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

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


def lin_a98rgb_to_xyz(rgb: Vector) -> MutableVector:
    """
    Convert an array of linear-light a98-rgb values to CIE XYZ using D50.D65.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    which has greater numerical precision than section 4.3.5.3 of
    https://www.adobe.com/digitalimag/pdfs/AdobeRGB1998.pdf
    """

    return cast(MutableVector, util.dot(RGB_TO_XYZ, rgb))


def xyz_to_lin_a98rgb(xyz: Vector) -> MutableVector:
    """Convert XYZ to linear-light a98-rgb."""

    return cast(MutableVector, util.dot(XYZ_TO_RGB, xyz))


def lin_a98rgb(rgb: Vector) -> MutableVector:
    """Convert an array of a98-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return [util.npow(val, 563 / 256) for val in rgb]


def gam_a98rgb(rgb: Vector) -> MutableVector:
    """Convert an array of linear-light a98-rgb  in the range 0.0-1.0 to gamma corrected form."""

    return [util.npow(val, 256 / 563) for val in rgb]


class A98RGB(SRGB):
    """A98 RGB class."""

    SPACE = "a98-rgb"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE, channels=3))
    WHITE = "D65"

    @classmethod
    def _to_xyz(cls, parent: 'Color', rgb: Vector) -> MutableVector:
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lin_a98rgb_to_xyz(lin_a98rgb(rgb)))

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """From XYZ."""

        return gam_a98rgb(xyz_to_lin_a98rgb(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz)))
