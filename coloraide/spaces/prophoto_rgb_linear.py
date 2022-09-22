"""Linear Pro Photo RGB color class."""
from __future__ import annotations
from ..cat import WHITES
from .srgb import sRGB
from .. import algebra as alg
from ..types import Vector

RGB_TO_XYZ = [
    [0.7977604896723027, 0.13518583717574031, 0.0313493495815248],
    [0.2880711282292934, 0.7118432178101014, 8.565396060525902e-05],
    [0.0, 0.0, 0.8251046025104601]
]

XYZ_TO_RGB = [
    [1.3457989731028281, -0.2555801000799754, -0.05110628506753401],
    [-0.5446224939028347, 1.5082327413132781, 0.02053603239147973],
    [0.0, 0.0, 1.2119675456389454]
]


def lin_prophoto_to_xyz(rgb: Vector) -> Vector:
    """
    Convert an array of linear-light prophoto-rgb values to CIE XYZ using  D50.D50.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    return alg.dot(RGB_TO_XYZ, rgb, dims=alg.D2_D1)


def xyz_to_lin_prophoto(xyz: Vector) -> Vector:
    """Convert XYZ to linear-light prophoto-rgb."""

    return alg.dot(XYZ_TO_RGB, xyz, dims=alg.D2_D1)


class ProPhotoRGBLinear(sRGB):
    """Linear Pro Photo RGB class."""

    BASE = "xyz-d50"
    NAME = "prophoto-rgb-linear"
    SERIALIZE = ('--prophoto-rgb-linear',)
    WHITE = WHITES['2deg']['D50']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Linear Pro Photo RGB."""

        return lin_prophoto_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Linear Pro Photo RGB."""

        return xyz_to_lin_prophoto(coords)
