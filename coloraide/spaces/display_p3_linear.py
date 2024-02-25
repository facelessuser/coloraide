"""Linear Display-p3 color class."""
from __future__ import annotations
from .srgb_linear import sRGBLinear
from .. import algebra as alg
from ..types import Vector

RGB_TO_XYZ = [
    [0.48657094864821615, 0.26566769316909306, 0.19821728523436247],
    [0.22897456406974878, 0.6917385218365063, 0.07928691409374498],
    [-3.9720755169334874e-17, 0.04511338185890263, 1.0439443689009757]
]

XYZ_TO_RGB = [
    [2.4934969119414254, -0.931383617919124, -0.4027107844507169],
    [-0.8294889695615748, 1.7626640603183465, 0.023624685841943587],
    [0.03584583024378447, -0.07617238926804183, 0.9568845240076874]
]


def lin_p3_to_xyz(rgb: Vector) -> Vector:
    """
    Convert an array of linear-light image-p3 values to CIE XYZ using  D65 (no chromatic adaptation).

    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    # 0 was computed as -3.972075516933488e-17
    return alg.matmul(RGB_TO_XYZ, rgb, dims=alg.D2_D1)


def xyz_to_lin_p3(xyz: Vector) -> Vector:
    """Convert XYZ to linear-light P3."""

    return alg.matmul(XYZ_TO_RGB, xyz, dims=alg.D2_D1)


class DisplayP3Linear(sRGBLinear):
    """Linear Display-p3 class."""

    BASE = "xyz-d65"
    NAME = "display-p3-linear"
    SERIALIZE = ('--display-p3-linear',)

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Linear Display P3."""

        return lin_p3_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Linear Display P3."""

        return xyz_to_lin_p3(coords)
