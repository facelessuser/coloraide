"""A98 RGB color class."""
from ..spaces import RE_DEFAULT_MATCH
from ..spaces import _cat
from .srgb import SRGB
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
        [0.5767308871981476, 0.1855539507112141, 0.1881851620906385],
        [0.2973768637115448, 0.6273490714522, 0.0752740648362554],
        [0.0270342603374131, 0.0706872193185578, 0.9911085203440293]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_a98rgb(xyz):
    """Convert XYZ to linear-light a98-rgb."""

    m = [
        [2.04136897926008, -0.5649463871751959, -0.3446943843778484],
        [-0.9692660305051867, 1.8760108454466937, 0.0415560175303498],
        [0.0134473872161703, -0.1183897423541256, 1.0154095719504166]
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
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = _cat.WHITES["D65"]

    @classmethod
    def _to_xyz(cls, rgb):
        """To XYZ."""

        return _cat.chromatic_adaption(cls.white(), XYZ.white(), lin_a98rgb_to_xyz(lin_a98rgb(rgb)))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return gam_a98rgb(xyz_to_lin_a98rgb(_cat.chromatic_adaption(XYZ.white(), cls.white(), xyz)))
