"""Pro Photo RGB color class."""
from __future__ import annotations
from ..cat import WHITES
from .srgb import sRGB
from .. import algebra as alg
from ..types import Vector

ET = 1 / 512
ET2 = 16 / 512


def lin_prophoto(rgb: Vector) -> Vector:
    """
    Convert an array of prophoto-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form.

    Transfer curve is gamma 1.8 with a small linear portion.

    https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        if abs(i) < ET2:
            result.append(i / 16.0)
        else:
            result.append(alg.npow(i, 1.8))
    return result


def gam_prophoto(rgb: Vector) -> Vector:
    """
    Convert an array of linear-light prophoto-rgb  in the range 0.0-1.0 to gamma corrected form.

    Transfer curve is gamma 1.8 with a small linear portion.

    https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        if abs(i) < ET:
            result.append(16.0 * i)
        else:
            result.append(alg.nth_root(i, 1.8))
    return result


class ProPhotoRGB(sRGB):
    """Pro Photo RGB class."""

    BASE = "prophoto-rgb-linear"
    NAME = "prophoto-rgb"
    WHITE = WHITES['2deg']['D50']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Pro Photo RGB."""

        return lin_prophoto(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Pro Photo RGB."""

        return gam_prophoto(coords)
