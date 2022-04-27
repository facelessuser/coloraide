"""A98 RGB color class."""
from ..cat import WHITES
from .srgb import SRGB
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


def lin_a98rgb(rgb: Vector) -> Vector:
    """Convert an array of a98-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return [alg.npow(val, 563 / 256) for val in rgb]


def gam_a98rgb(rgb: Vector) -> Vector:
    """Convert an array of linear-light a98-rgb  in the range 0.0-1.0 to gamma corrected form."""

    return [alg.npow(val, 256 / 563) for val in rgb]


class A98RGB(SRGB):
    """A98 RGB class."""

    BASE = "xyz-d65"
    NAME = "a98-rgb"
    WHITE = WHITES['2deg']['D65']

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To XYZ from A98 RGB."""

        return lin_a98rgb_to_xyz(lin_a98rgb(coords))

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From XYZ to A98 RGB."""

        return gam_a98rgb(xyz_to_lin_a98rgb(coords))
