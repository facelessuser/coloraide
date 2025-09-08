"""
Rec. 709 color space class (display-referred).

Uses the display referred EOTF as specified in BT.1886.

This color space uses the same chromaticities and white points as sRGB,
but uses the same gamma correction as Rec. 2020.

- https://en.wikipedia.org/wiki/Rec._709
- https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.709-6-201506-I!!PDF-E.pdf
- https://www.itu.int/dms_pubrec/itu-r/rec/bt/r-rec-bt.1886-0-201103-i!!pdf-e.pdf
"""
from __future__ import annotations
from .srgb_linear import sRGBLinear
from .rec2020 import inverse_eotf_bt1886, eotf_bt1886
from ..types import Vector


class Rec709(sRGBLinear):
    """Rec. 709 class Using the display-referred EOTF as specified in BT.1886."""

    BASE = "srgb-linear"
    NAME = "rec709"
    SERIALIZE = ("--rec709",)

    def linear(self) -> str:
        """Return linear version of the RGB (if available)."""

        return self.BASE

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Rec. 709."""

        return eotf_bt1886(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Rec. 709."""

        return inverse_eotf_bt1886(coords)
