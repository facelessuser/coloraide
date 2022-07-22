"""DIN99o LCh class."""
from ..cat import WHITES
from .lch import LCh
from .. import util
import math
from .. import algebra as alg
from ..types import Vector
from ..channels import Channel, FLG_ANGLE

ACHROMATIC_THRESHOLD = 0.0000000002


def lch_to_lab(lch: Vector) -> Vector:
    """DIN99o LCh to lab."""

    l, c, h = lch
    if alg.is_nan(h):  # pragma: no cover
        return [l, 0.0, 0.0]

    return [
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    ]


def lab_to_lch(lab: Vector) -> Vector:
    """DIN99o Lab to LCh."""

    l, a, b = lab
    h = math.degrees(math.atan2(b, a))
    c = math.sqrt(a ** 2 + b ** 2)

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c <= ACHROMATIC_THRESHOLD:
        h = alg.NaN

    return [l, c, util.constrain_hue(h)]


class LCh99o(LCh):
    """DIN99o LCh class."""

    BASE = 'din99o'
    NAME = "lch99o"
    SERIALIZE = ("--lch99o",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("c", 0.0, 60.0, limit=(0.0, None)),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )

    def to_base(self, coords: Vector) -> Vector:
        """To DIN99o from DIN99o LCh."""

        return lch_to_lab(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From DIN99o to DIN99o LCh."""

        return lab_to_lch(coords)
