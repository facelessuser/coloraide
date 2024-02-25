"""sRGB color class."""
from __future__ import annotations
from ..srgb_linear import sRGBLinear
from ... import algebra as alg
from ...types import Vector
import math


def lin_srgb(rgb: Vector) -> Vector:
    """
    Convert an array of sRGB values in the range 0.0 - 1.0 to linear light (un-corrected) form.

    https://en.wikipedia.org/wiki/SRGB
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i > 0.04045:
            result.append(math.copysign(((abs_i + 0.055) / 1.055) ** 2.4, i))
        else:
            result.append(i / 12.92)
    return result


def gam_srgb(rgb: Vector) -> Vector:
    """
    Convert an array of linear-light sRGB values in the range 0.0-1.0 to gamma corrected form.

    https://en.wikipedia.org/wiki/SRGB
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i > 0.0031308:
            result.append(math.copysign(1.055 * (alg.nth_root(abs_i, 2.4)) - 0.055, i))
        else:
            result.append(12.92 * i)
    return result


class sRGB(sRGBLinear):
    """sRGB class."""

    BASE = "srgb-linear"
    NAME = "srgb"
    SERIALIZE = ("srgb",)
    EXTENDED_RANGE = True

    def linear(self) -> str:
        """Return linear version of the RGB (if available)."""

        return self.BASE

    def from_base(self, coords: Vector) -> Vector:
        """From sRGB Linear to sRGB."""

        return gam_srgb(coords)

    def to_base(self, coords: Vector) -> Vector:
        """To sRGB Linear from sRGB."""

        return lin_srgb(coords)
