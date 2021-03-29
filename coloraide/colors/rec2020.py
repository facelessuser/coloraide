"""Rec 2020 color class."""
from ._space import RE_DEFAULT_MATCH
from .srgb import SRGB
from .xyz import XYZ
from . import _convert as convert
from .. import util
import re
import math

ALPHA = 1.09929682680944
BETA = 0.018053968510807
BETA45 = 0.018053968510807 * 4.5


def lin_2020(rgb):
    """
    Convert an array of rec-2020 RGB values in the range 0.0 - 1.0 to linear light (un-corrected) form.

    https://en.wikipedia.org/wiki/Rec._2020#Transfer_characteristics
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i < BETA45:
            result.append(i / 4.5)
        else:
            result.append(math.copysign(((abs_i + ALPHA - 1) / ALPHA) ** (1 / 0.45), i))
    return result


def gam_2020(rgb):
    """
    Convert an array of linear-light rec-2020 RGB  in the range 0.0-1.0 to gamma corrected form.

    https://en.wikipedia.org/wiki/Rec._2020#Transfer_characteristics
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i < BETA:
            result.append(4.5 * i)
        else:
            result.append(math.copysign(ALPHA * abs_i ** 0.45 - (ALPHA - 1), i))
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
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D65"]

    @classmethod
    def _to_xyz(cls, rgb):
        """To XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lin_2020_to_xyz(lin_2020(rgb)))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return gam_2020(xyz_to_lin_2020(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz)))
