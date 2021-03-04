"""Pro Photo RGB color class."""
from ._space import RE_DEFAULT_MATCH
from .srgb import SRGB
from . import _convert as convert
from .. import util
import re
import math


def lin_prophoto_to_xyz(rgb):
    """
    Convert an array of linear-light prophoto-rgb values to CIE XYZ using  D50.D50.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [0.7977604896723027, 0.13518583717574031, 0.0313493495815248],
        [0.2880711282292934, 0.7118432178101014, 0.00008565396060525902],
        [0.0, 0.0, 0.8251046025104601]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_prophoto(xyz):
    """Convert XYZ to linear-light prophoto-rgb."""

    m = [
        [1.3457989731028281, -0.25558010007997534, -0.05110628506753401],
        [-0.5446224939028347, 1.5082327413132781, 0.02053603239147973],
        [0.0, 0.0, 1.2119675456389454]
    ]

    return util.dot(m, xyz)


def lin_prophoto(rgb):
    """
    Convert an array of prophoto-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form.

    Transfer curve is gamma 1.8 with a small linear portion.
    """

    et2 = 16 / 512

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i <= et2:
            result.append(i / 16)
        else:
            result.append(math.copysign(math.pow(abs_i, 1.8), i))
    return result


def gam_prophoto(rgb):
    """
    Convert an array of linear-light prophoto-rgb  in the range 0.0-1.0 to gamma corrected form.

    Transfer curve is gamma 1.8 with a small linear portion.
    """

    et = 1 / 512

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i >= et:
            result.append(math.copysign(math.pow(abs_i, 1 / 1.8), i))
        else:
            result.append(16 * i)
    return result


class ProPhoto_RGB(SRGB):
    """Pro Photo RGB class."""

    SPACE = "prophoto-rgb"
    DEF_VALUE = "color(prophoto-rgb 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D50"]

    def __init__(self, color=DEF_VALUE):
        """Initialize."""

        super().__init__(color)

    @classmethod
    def _to_xyz(cls, rgb):
        """To XYZ."""

        return lin_prophoto_to_xyz(lin_prophoto(rgb))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return gam_prophoto(xyz_to_lin_prophoto(xyz))
