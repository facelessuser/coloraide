"""A98 RGB color class."""
from ..spaces import RE_DEFAULT_MATCH
from .srgb.base import SRGB
from .xyz import XYZ
from .. import util
import re


def lin_a98rgb_to_xyz(rgb):
    """
    Convert an array of linear-light a98-rgb values to CIE XYZ using D50.D65.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    which has greater numerical precision than section 4.3.5.3 of
    https://www.adobe.com/digitalimag/pdfs/AdobeRGB1998.pdf
    """

    m = [
        [0.5767308871981476, 0.18555395071121408, 0.18818516209063846],
        [0.2973768637115448, 0.6273490714522, 0.07527406483625539],
        [0.027034260337413137, 0.0706872193185578, 0.9911085203440293]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_a98rgb(xyz):
    """Convert XYZ to linear-light a98-rgb."""

    m = [
        [2.04136897926008, -0.5649463871751959, -0.34469438437784844],
        [-0.9692660305051867, 1.8760108454466937, 0.04155601753034983],
        [0.013447387216170269, -0.11838974235412557, 1.0154095719504166]
    ]

    return util.dot(m, xyz)


def lin_a98rgb(rgb):
    """Convert an array of a98-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return [util.npow(val, 563 / 256) for val in rgb]


def gam_a98rgb(rgb):
    """Convert an array of linear-light a98-rgb  in the range 0.0-1.0 to gamma corrected form."""

    return [util.npow(val, 256 / 563) for val in rgb]


class A98RGB(SRGB):
    """A98 RGB class."""

    SPACE = "a98-rgb"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE, channels=3))
    WHITE = "D65"

    @classmethod
    def _to_xyz(cls, parent, rgb):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lin_a98rgb_to_xyz(lin_a98rgb(rgb)))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return gam_a98rgb(xyz_to_lin_a98rgb(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz)))
