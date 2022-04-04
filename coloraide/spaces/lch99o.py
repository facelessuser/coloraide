"""Din99o Lch class."""
from ..cat import WHITES
from .lch import Lch
from .. import util
import math
from .. import algebra as alg
from ..types import Vector

ACHROMATIC_THRESHOLD = 0.0000000002


def lch_to_lab(lch: Vector) -> Vector:
    """Din99o Lch to lab."""

    l, c, h = lch
    if alg.is_nan(h):  # pragma: no cover
        return [l, 0.0, 0.0]

    return [
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    ]


def lab_to_lch(lab: Vector) -> Vector:
    """Din99o Lab to Lch."""

    l, a, b = lab
    h = math.degrees(math.atan2(b, a))
    c = math.sqrt(a ** 2 + b ** 2)

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c <= ACHROMATIC_THRESHOLD:
        h = alg.NaN

    return [l, c, util.constrain_hue(h)]


class Lch99o(Lch):
    """Din99o Lch class."""

    BASE = 'din99o'
    NAME = "lch99o"
    SERIALIZE = ("--lch99o",)
    WHITE = WHITES['2deg']['D65']

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To Din99o from Din99o Lch."""

        return lch_to_lab(coords)

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From Din99o to Din99o Lch."""

        return lab_to_lch(coords)
