"""Pro Photo RGB color class."""
from ._space import RE_DEFAULT_MATCH
from .srgb import SRGB
from .xyz import XYZ
from . import _convert as convert
from .. import util
import re
import math

ET = 1 / 512
ET2 = 16 / 512


def lin_prophoto_to_xyz(rgb):
    """
    Convert an array of linear-light prophoto-rgb values to CIE XYZ using  D50.D50.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [7.9776048967230273e-01, 1.3518583717574034e-01, 3.1349349581524806e-02],
        [2.8807112822929343e-01, 7.1184321781010151e-01, 8.5653960605259035e-05],
        [0.0000000000000000e+00, 0.0000000000000000e+00, 8.2510460251046025e-01]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_prophoto(xyz):
    """Convert XYZ to linear-light prophoto-rgb."""

    m = [
        [1.345798973102828, -0.2555801000799754, -0.051106285067534],
        [-0.5446224939028346, 1.508232741313278, 0.0205360323914797],
        [0.0, 0.0, 1.2119675456389452]
    ]

    return util.dot(m, xyz)


def lin_prophoto(rgb):
    """
    Convert an array of prophoto-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form.

    Transfer curve is gamma 1.8 with a small linear portion.

    https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i < ET2:
            result.append(i / 16.0)
        else:
            result.append(math.copysign(abs_i ** 1.8, i))
    return result


def gam_prophoto(rgb):
    """
    Convert an array of linear-light prophoto-rgb  in the range 0.0-1.0 to gamma corrected form.

    Transfer curve is gamma 1.8 with a small linear portion.

    https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i < ET:
            result.append(16.0 * i)
        else:
            result.append(math.copysign(abs_i ** (1.0 / 1.8), i))
    return result


class ProPhotoRGB(SRGB):
    """Pro Photo RGB class."""

    SPACE = "prophoto-rgb"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D50"]

    @classmethod
    def _to_xyz(cls, rgb):
        """To XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lin_prophoto_to_xyz(lin_prophoto(rgb)))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return gam_prophoto(xyz_to_lin_prophoto(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz)))
