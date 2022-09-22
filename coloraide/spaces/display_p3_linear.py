"""Linear Display-p3 color class."""
from __future__ import annotations
from ..cat import WHITES
from .srgb import sRGB
from .. import algebra as alg
from ..types import Vector

RGB_TO_XYZ = [
    [0.4865709486482161, 0.26566769316909306, 0.1982172852343625],
    [0.22897456406974875, 0.6917385218365063, 0.079286914093745],
    [-3.972075516933487e-17, 0.04511338185890263, 1.043944368900976]
]

XYZ_TO_RGB = [
    [2.4934969119414254, -0.9313836179191239, -0.40271078445071684],
    [-0.8294889695615747, 1.7626640603183465, 0.02362468584194358],
    [0.03584583024378446, -0.0761723892680418, 0.9568845240076872]
]


def lin_p3_to_xyz(rgb: Vector) -> Vector:
    """
    Convert an array of linear-light image-p3 values to CIE XYZ using  D65 (no chromatic adaptation).

    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    # 0 was computed as -3.972075516933488e-17
    return alg.dot(RGB_TO_XYZ, rgb, dims=alg.D2_D1)


def xyz_to_lin_p3(xyz: Vector) -> Vector:
    """Convert XYZ to linear-light P3."""

    return alg.dot(XYZ_TO_RGB, xyz, dims=alg.D2_D1)


class DisplayP3Linear(sRGB):
    """Linear Display-p3 class."""

    BASE = "xyz-d65"
    NAME = "display-p3-linear"
    SERIALIZE = ('--display-p3-linear',)
    WHITE = WHITES['2deg']['D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Linear Display P3."""

        return lin_p3_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Linear Display P3."""

        return xyz_to_lin_p3(coords)
