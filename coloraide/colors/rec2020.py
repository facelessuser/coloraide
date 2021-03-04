"""Rec 2020 color class."""
from ._space import RE_DEFAULT_MATCH
from .srgb import SRGB
from .xyz import XYZ
from . import _convert as convert
from .. import util
import re
import math


def lin_2020(rgb):
    """Convert an array of rec-2020 RGB values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    alpha = 1.09929682680944
    beta = 0.018053968510807

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i < beta * 4.5:
            result.append(i / 4.5)
        else:
            result.append(math.copysign(math.pow((abs_i + alpha - 1) / alpha, 1 / 0.45), i))
    return result


def gam_2020(rgb):
    """Convert an array of linear-light rec-2020 RGB  in the range 0.0-1.0 to gamma corrected form."""

    alpha = 1.09929682680944
    beta = 0.018053968510807

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i > beta:
            result.append(math.copysign(alpha * math.pow(abs_i, 0.45) - (alpha - 1), i))
        else:
            result.append(4.5 * i)
    return result


def lin_2020_to_xyz(rgb):
    """
    Convert an array of linear-light rec-2020 values to CIE XYZ using  D65.

    (no chromatic adaptation)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [0.6369580483012914, 0.14461690358620832, 0.1688809751641721],
        [0.2627002120112671, 0.6779980715188708, 0.05930171646986196],
        [0.000000000000000, 0.028072693049087428, 1.060985057710791]
    ]

    # 0 is actually calculated as 4.994106574466076e-17
    return util.dot(m, rgb)


def xyz_to_lin_2020(xyz):
    """Convert XYZ to linear-light rec-2020."""

    m = [
        [1.7166511879712674, -0.35567078377639233, -0.25336628137365974],
        [-0.6666843518324892, 1.6164812366349395, 0.01576854581391113],
        [0.017639857445310783, -0.042770613257808524, 0.9421031212354738]
    ]

    return util.dot(m, xyz)


class Rec2020(SRGB):
    """Rec 2020 class."""

    SPACE = "rec2020"
    DEF_VALUE = "color(rec2020 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D65"]

    def __init__(self, color=DEF_VALUE):
        """Initialize."""

        super().__init__(color)

    @classmethod
    def _to_xyz(cls, rgb):
        """To XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lin_2020_to_xyz(lin_2020(rgb)))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return gam_2020(xyz_to_lin_2020(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz)))
