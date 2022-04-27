"""Rec 2020 color class."""
from ..cat import WHITES
from .srgb import SRGB
import math
from .. import algebra as alg
from ..types import Vector

ALPHA = 1.09929682680944
BETA = 0.018053968510807
BETA45 = 0.018053968510807 * 4.5

RGB_TO_XYZ = [
    [0.6369580483012914, 0.14461690358620832, 0.16888097516417208],
    [0.2627002120112671, 0.6779980715188708, 0.05930171646986195],
    [4.994106574466076e-17, 0.028072693049087428, 1.0609850577107909]
]

XYZ_TO_RGB = [
    [1.7166511879712674, -0.35567078377639233, -0.25336628137365974],
    [-0.6666843518324892, 1.6164812366349395, 0.015768545813911124],
    [0.017639857445310787, -0.04277061325780853, 0.9421031212354739]
]


def lin_2020(rgb: Vector) -> Vector:
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
            result.append(math.copysign(alg.nth_root((abs_i + ALPHA - 1) / ALPHA, 0.45), i))
    return result


def gam_2020(rgb: Vector) -> Vector:
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


def lin_2020_to_xyz(rgb: Vector) -> Vector:
    """
    Convert an array of linear-light rec-2020 values to CIE XYZ using  D65.

    (no chromatic adaptation)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    return alg.dot(RGB_TO_XYZ, rgb, dims=alg.D2_D1)


def xyz_to_lin_2020(xyz: Vector) -> Vector:
    """Convert XYZ to linear-light rec-2020."""

    return alg.dot(XYZ_TO_RGB, xyz, dims=alg.D2_D1)


class Rec2020(SRGB):
    """Rec 2020 class."""

    BASE = "xyz-d65"
    NAME = "rec2020"
    WHITE = WHITES['2deg']['D65']

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To XYZ from Rec 2020."""

        return lin_2020_to_xyz(lin_2020(coords))

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From XYZ to Rec 2020."""

        return gam_2020(xyz_to_lin_2020(coords))
