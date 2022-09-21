"""Linear A98 RGB color class."""
from __future__ import annotations
from ..cat import WHITES
from .srgb import sRGB
from .. import algebra as alg
from ..types import Vector

RGB_TO_XYZ = [
    [0.5766690429101305, 0.1855582379065463, 0.1882286462349947],
    [0.29734497525053605, 0.6273635662554661, 0.07529145849399788],
    [0.02703136138641234, 0.07068885253582723, 0.9913375368376388]
]

XYZ_TO_RGB = [
    [2.0415879038107465, -0.5650069742788596, -0.34473135077832956],
    [-0.9692436362808795, 1.8759675015077202, 0.04155505740717558],
    [0.013444280632031142, -0.11836239223101837, 1.0151749943912054]
]


def lin_a98rgb_to_xyz(rgb: Vector) -> Vector:
    """
    Convert an array of linear-light a98-rgb values to CIE XYZ using D50.D65.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    which has greater numerical precision than section 4.3.5.3 of
    https://www.adobe.com/digitalimag/pdfs/AdobeRGB1998.pdf
    """

    return alg.dot(RGB_TO_XYZ, rgb, dims=alg.D2_D1)


def xyz_to_lin_a98rgb(xyz: Vector) -> Vector:
    """Convert XYZ to linear-light a98-rgb."""

    return alg.dot(XYZ_TO_RGB, xyz, dims=alg.D2_D1)


class A98RGBLinear(sRGB):
    """Linear A98 RGB class."""

    BASE = "xyz-d65"
    NAME = "a98-rgb-linear"
    SERIALIZE = ('--a98-rgb-linear',)
    WHITE = WHITES['2deg']['D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from A98 RGB."""

        return lin_a98rgb_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to A98 RGB."""

        return xyz_to_lin_a98rgb(coords)
