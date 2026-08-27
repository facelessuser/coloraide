"""Linear Pro Photo RGB color class."""
from __future__ import annotations
from ..cat import WHITES
from .srgb_linear import RGB
from .. import algebra as alg
from ..types import Vector

RGB_TO_XYZ = [
    [7.9776048967230260e-01, 1.3518583717574031e-01, 3.1349349581524806e-02],
    [2.8807112822929337e-01, 7.1184321781010140e-01, 8.5653960605259030e-05],
    [0.0000000000000000e+00, 0.0000000000000000e+00, 8.2510460251046020e-01]
]

XYZ_TO_RGB = [
    [ 1.3457989731028281 , -0.2555801000799754 , -0.05110628506753401],
    [-0.5446224939028347 ,  1.5082327413132781 ,  0.02053603239147973],
    [ 0.                 ,  0.                 ,  1.2119675456389452 ]
]


def lin_prophoto_to_xyz(rgb: Vector) -> Vector:
    """
    Convert an array of linear-light prophoto-rgb values to CIE XYZ using  D50.D50.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    return alg.matmul_x3(RGB_TO_XYZ, rgb, dims=alg.D2_D1)


def xyz_to_lin_prophoto(xyz: Vector) -> Vector:
    """Convert XYZ to linear-light prophoto-rgb."""

    return alg.matmul_x3(XYZ_TO_RGB, xyz, dims=alg.D2_D1)


class ProPhotoRGBLinear(RGB):
    """Linear Pro Photo RGB class."""

    BASE = "xyz-d50"
    NAME = "prophoto-rgb-linear"
    SERIALIZE = ('--prophoto-rgb-linear',)
    WHITE = WHITES['2deg']['D50']
    TO_XYZ = RGB_TO_XYZ
    TO_RGB = XYZ_TO_RGB

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Linear Pro Photo RGB."""

        return lin_prophoto_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Linear Pro Photo RGB."""

        return xyz_to_lin_prophoto(coords)
