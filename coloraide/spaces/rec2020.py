"""
Rec. 2020 color space.

Uses the display referred EOTF as specified in BT.1886.

- https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.2020-2-201510-I!!PDF-E.pdf
- https://www.itu.int/dms_pubrec/itu-r/rec/bt/r-rec-bt.1886-0-201103-i!!pdf-e.pdf
"""
from __future__ import annotations
from .srgb_linear import sRGBLinear
import math
from .. import algebra as alg
from ..types import Vector


def inverse_eotf_bt1886(rgb: Vector, lb: float = 0, lw: float = 1.0, gamma: float = 2.40) -> Vector:
    """Inverse ITU-R BT.1886 EOTF."""

    igamma = 1 / gamma

    d = lw ** igamma - lb ** igamma
    a = d ** gamma
    b = lb ** igamma / d
    return [math.copysign(a * alg.spow(abs(l) / a, igamma) - b, l) for l in rgb]


def eotf_bt1886(rgb: Vector, lb: float = 0, lw: float = 1.0, gamma: float = 2.40) -> Vector:
    """ITU-R BT.1886 EOTF."""

    igamma = 1 / gamma

    d = lw ** igamma - lb ** igamma
    a = d ** gamma
    b = lb ** igamma / d
    return [math.copysign(a * alg.spow(max(abs(v) + b, 0), gamma), v) for v in rgb]


class Rec2020(sRGBLinear):
    """Rec 2020 class."""

    BASE = "rec2020-linear"
    NAME = "rec2020"

    def linear(self) -> str:
        """Return linear version of the RGB (if available)."""

        return self.BASE

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Rec. 2020."""

        return eotf_bt1886(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Rec. 2020."""

        return inverse_eotf_bt1886(coords)
