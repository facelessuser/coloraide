"""Rec 2020 color class."""
from ..spaces import RE_DEFAULT_MATCH
from .srgb import SRGB
from .. import util
import re
import math
from ..util import MutableVector
from typing import cast

ALPHA = 1.09929682680944
BETA = 0.018053968510807
BETA45 = 0.018053968510807 * 4.5

RGB_TO_XYZ = [
    [6.3695804830129132e-01, 1.4461690358620838e-01, 1.6888097516417216e-01],
    [2.6270021201126703e-01, 6.7799807151887104e-01, 5.9301716469861973e-02],
    [4.9941065744660755e-17, 2.8072693049087438e-02, 1.0609850577107913e+00]
]

XYZ_TO_RGB = [
    [1.7166511879712676, -0.3556707837763924, -0.2533662813736598],
    [-0.6666843518324889, 1.6164812366349388, 0.01576854581391115],
    [0.01763985744531078, -0.04277061325780851, 0.9421031212354736]
]


def lin_2020(rgb: MutableVector) -> MutableVector:
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
            result.append(math.copysign(util.nth_root((abs_i + ALPHA - 1) / ALPHA, 0.45), i))
    return result


def gam_2020(rgb: MutableVector) -> MutableVector:
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
            result.append(math.copysign(ALPHA * (abs_i ** 0.45) - (ALPHA - 1), i))
    return result


def lin_2020_to_xyz(rgb: MutableVector) -> MutableVector:
    """
    Convert an array of linear-light rec-2020 values to CIE XYZ using  D65.

    (no chromatic adaptation)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    return cast(MutableVector, util.dot(RGB_TO_XYZ, rgb))


def xyz_to_lin_2020(xyz: MutableVector) -> MutableVector:
    """Convert XYZ to linear-light rec-2020."""

    return cast(MutableVector, util.dot(XYZ_TO_RGB, xyz))


class Rec2020(SRGB):
    """Rec 2020 class."""

    BASE = "xyz"
    NAME = "rec2020"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=NAME, channels=3))
    WHITE = "D65"

    @classmethod
    def to_base(cls, coords: MutableVector) -> MutableVector:
        """To XYZ from Rec 2020."""

        return lin_2020_to_xyz(lin_2020(coords))

    @classmethod
    def from_base(cls, coords: MutableVector) -> MutableVector:
        """From XYZ to Rec 2020."""

        return gam_2020(xyz_to_lin_2020(coords))
