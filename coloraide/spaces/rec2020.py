"""Rec 2020 color class."""
from ..spaces import RE_DEFAULT_MATCH
from .srgb.base import SRGB
from .xyz import XYZ
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
            result.append(math.copysign(util.nth_root((abs_i + ALPHA - 1) / ALPHA, 0.45), i))
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
            result.append(math.copysign(ALPHA * (abs_i ** 0.45) - (ALPHA - 1), i))
    return result


def lin_2020_to_xyz(rgb):
    """
    Convert an array of linear-light rec-2020 values to CIE XYZ using  D65.

    (no chromatic adaptation)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [6.3701019141110093e-01, 1.4461502739696933e-01, 1.6884478119192992e-01],
        [2.6272171736164052e-01, 6.7798927550226207e-01, 5.9289007136097520e-02],
        [4.9945154055471928e-17, 2.8072328847646915e-02, 1.0607576711523534e+00]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_2020(xyz):
    """Convert XYZ to linear-light rec-2020."""

    m = [
        [1.7165106697619734, -0.35564166998671587, -0.25334554182190716],
        [-0.6666930011826241, 1.6165022083469103, 0.015768750389995],
        [0.017643638767459002, -0.04277978166904461, 0.9423050727200183]
    ]

    return util.dot(m, xyz)


class Rec2020(SRGB):
    """Rec 2020 class."""

    SPACE = "rec2020"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE, channels=3))
    WHITE = "D65"

    @classmethod
    def _to_xyz(cls, parent, rgb):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lin_2020_to_xyz(lin_2020(rgb)))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return gam_2020(xyz_to_lin_2020(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz)))
