"""
Rec. 709 color space class.

This color space uses the same chromaticities and white points as sRGB,
but uses the same gamma correction as Rec. 2020, just at 10 bit precision.

- https://en.wikipedia.org/wiki/Rec._709
- https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.709-6-201506-I!!PDF-E.pdf
"""
from __future__ import annotations
from .srgb import sRGB
import math
from .. import algebra as alg
from ..types import Vector

ALPHA = 1.099
BETA = 0.018
BETA45 = BETA * 4.5
ALPHAM1 = 0.099


def lin_709(rgb: Vector) -> Vector:
    """
    Convert an array of Rec. 709 RGB values in the range 0.0 - 1.0 to linear light (un-corrected) form.

    Transfer function is similar to Rec. 2020, just at a lower precision
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i < BETA45:
            result.append(i / 4.5)
        else:
            result.append(math.copysign(alg.nth_root((abs_i + ALPHAM1) / ALPHA, 0.45), i))
    return result


def gam_709(rgb: Vector) -> Vector:
    """
    Convert an array of linear-light Rec. 709 RGB  in the range 0.0-1.0 to gamma corrected form.

    Transfer function is similar to Rec. 2020, just at a lower precision
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i < BETA:
            result.append(4.5 * i)
        else:
            result.append(math.copysign(ALPHA * (abs_i ** 0.45) - ALPHAM1, i))
    return result


class Rec709(sRGB):
    """Rec. 709 class."""

    BASE = "srgb-linear"
    NAME = "rec709"
    SERIALIZE = ("--rec709",)

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Rec. 709."""

        return lin_709(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Rec. 709."""

        return gam_709(coords)
