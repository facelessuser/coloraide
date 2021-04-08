"""A98 RGB color class."""
from ._space import RE_DEFAULT_MATCH
from .srgb import SRGB
from .xyz import XYZ
from . import _convert as convert
from .. import util
import re
import math


def lin_a98rgb_to_xyz(rgb):
    """
    Convert an array of linear-light a98-rgb values to CIE XYZ using D50.D65.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    which has greater numerical precision than section 4.3.5.3 of
    https://www.adobe.com/digitalimag/pdfs/AdobeRGB1998.pdf
    """

    m = [
        [0.5766690429101304, 0.1855582379065464, 0.1882286462349947],
        [0.297344975250536, 0.6273635662554663, 0.0752914584939979],
        [0.0270313613864123, 0.0706888525358273, 0.9913375368376391]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_a98rgb(xyz):
    """Convert XYZ to linear-light a98-rgb."""

    m = [
        [2.041587903810747, -0.5650069742788599, -0.3447313507783297],
        [-0.9692436362808794, 1.8759675015077197, 0.0415550574071756],
        [0.0134442806320311, -0.1183623922310184, 1.0151749943912052]
    ]

    return util.dot(m, xyz)


def lin_a98rgb(rgb):
    """Convert an array of a98-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return [math.copysign(abs(val) ** (563 / 256), val) for val in rgb]


def gam_a98rgb(rgb):
    """Convert an array of linear-light a98-rgb  in the range 0.0-1.0 to gamma corrected form."""

    return [math.copysign(abs(val) ** (256 / 563), val) for val in rgb]


class A98RGB(SRGB):
    """A98 RGB class."""

    SPACE = "a98-rgb"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D65"]

    @classmethod
    def _to_xyz(cls, rgb):
        """To XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lin_a98rgb_to_xyz(lin_a98rgb(rgb)))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return gam_a98rgb(xyz_to_lin_a98rgb(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz)))
