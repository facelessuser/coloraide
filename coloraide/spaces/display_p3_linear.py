"""Linear Display-p3 color class."""
from __future__ import annotations
from .srgb_linear import RGB
from .. import algebra as alg
from ..types import Vector

RGB_TO_XYZ = [
    [ 4.8657094864821615e-01,  2.6566769316909306e-01,  1.9821728523436247e-01],
    [ 2.2897456406974878e-01,  6.9173852183650630e-01,  7.9286914093744980e-02],
    [-3.9720755169334874e-17,  4.5113381858902630e-02,  1.0439443689009757e+00]
]

XYZ_TO_RGB = [
    [ 2.4934969119414254  , -0.931383617919124   , -0.4027107844507169  ],
    [-0.8294889695615748  ,  1.7626640603183465  ,  0.023624685841943587],
    [ 0.03584583024378447 , -0.07617238926804183 ,  0.9568845240076874  ]
]


def lin_p3_to_xyz(rgb: Vector) -> Vector:
    """
    Convert an array of linear-light image-p3 values to CIE XYZ using  D65 (no chromatic adaptation).

    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    # 0 was computed as -3.972075516933488e-17
    return alg.matmul_x3(RGB_TO_XYZ, rgb, dims=alg.D2_D1)


def xyz_to_lin_p3(xyz: Vector) -> Vector:
    """Convert XYZ to linear-light P3."""

    return alg.matmul_x3(XYZ_TO_RGB, xyz, dims=alg.D2_D1)


class DisplayP3Linear(RGB):
    """Linear Display-p3 class."""

    BASE = "xyz-d65"
    NAME = "display-p3-linear"
    SERIALIZE = ('display-p3-linear', '--display-p3-linear')
    TO_XYZ = RGB_TO_XYZ
    TO_RGB = XYZ_TO_RGB

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Linear Display P3."""

        return lin_p3_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Linear Display P3."""

        return xyz_to_lin_p3(coords)
