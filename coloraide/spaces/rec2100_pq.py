"""
Rec. 2100 PQ color class.

https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.2100-2-201807-I!!PDF-E.pdf
"""
from __future__ import annotations
from ..cat import WHITES
from .srgb_linear import sRGBLinear
from ..types import Vector
from .. import util


class Rec2100PQ(sRGBLinear):
    """Rec. 2100 PQ class."""

    BASE = "rec2100-linear"
    NAME = "rec2100-pq"
    SERIALIZE = ('rec2100-pq', '--rec2100-pq',)
    WHITE = WHITES['2deg']['D65']
    DYNAMIC_RANGE = 'hdr'

    def linear(self) -> str:
        """Return linear version of the RGB (if available)."""

        return self.BASE

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Rec. 2100 PQ."""

        return [max(c / util.YW, 0.0) for c in util.pq_st2084_eotf(coords)]

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Rec. 2100 PQ."""

        return util.pq_st2084_oetf([max(c * util.YW, 0.0) for c in coords])
