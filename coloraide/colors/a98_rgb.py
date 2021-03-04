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
        [0.5766690429101305, 0.1855582379065463, 0.1882286462349947],
        [0.29734497525053605, 0.6273635662554661, 0.07529145849399788],
        [0.02703136138641234, 0.07068885253582723, 0.9913375368376388]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_a98rgb(xyz):
    """Convert XYZ to linear-light a98-rgb."""

    m = [
        [2.0415879038107465, -0.5650069742788596, -0.34473135077832956],
        [-0.9692436362808795, 1.8759675015077202, 0.04155505740717557],
        [0.013444280632031142, -0.11836239223101838, 1.0151749943912054]
    ]

    return util.dot(m, xyz)


def lin_a98rgb(rgb):
    """Convert an array of a98-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return [math.copysign(math.pow(abs(val), 563 / 256), val) for val in rgb]


def gam_a98rgb(rgb):
    """Convert an array of linear-light a98-rgb  in the range 0.0-1.0 to gamma corrected form."""

    return [math.copysign(math.pow(abs(val), 256 / 563), val) for val in rgb]


class A98_RGB(SRGB):
    """A98 RGB class."""

    SPACE = "a98-rgb"
    DEF_VALUE = "color(a98-rgb 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D65"]

    def __init__(self, color=DEF_VALUE):
        """Initialize."""

        super().__init__(color)

    @classmethod
    def _to_xyz(cls, rgb):
        """To XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lin_a98rgb_to_xyz(lin_a98rgb(rgb)))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return gam_a98rgb(xyz_to_lin_a98rgb(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz)))
