"""Linear Rec 2020 color class."""
from __future__ import annotations
from ..cat import WHITES
from .srgb import sRGB
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


class Rec2020Linear(sRGB):
    """Linear Rec 2020 class."""

    BASE = "xyz-d65"
    NAME = "rec2020-linear"
    SERIALIZE = ('--rec2020-linear',)
    WHITE = WHITES['2deg']['D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Linear Rec 2020."""

        return lin_2020_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Linear Rec 2020."""

        return xyz_to_lin_2020(coords)
