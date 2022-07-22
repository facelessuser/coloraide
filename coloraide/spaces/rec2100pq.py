"""
Rec 2100 PQ color class.

https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.2100-2-201807-I!!PDF-E.pdf
"""
from ..cat import WHITES
from .srgb import sRGB
from .. import algebra as alg
from ..types import Vector
from .. import util


class Rec2100PQ(sRGB):
    """Rec 2100 PQ class."""

    BASE = "rec2020-linear"
    NAME = "rec2100pq"
    SERIALIZE = ('--rec2100pq',)
    WHITE = WHITES['2deg']['D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Rec 2100 PQ."""

        return alg.divide(util.pq_st2084_eotf(coords), util.YW, dims=alg.D1_SC)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Rec 2100 PQ."""

        return util.pq_st2084_inverse_eotf(alg.multiply(coords, util.YW, dims=alg.D1_SC))
