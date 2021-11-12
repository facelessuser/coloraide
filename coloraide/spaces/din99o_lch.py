"""Din99o Lch class."""
from ..spaces import RE_DEFAULT_MATCH
from .lch.base import LchBase
from .. import util
import math
import re
from ..util import Vector, MutableVector

ACHROMATIC_THRESHOLD = 0.0000000002


def lch_to_lab(lch: Vector) -> MutableVector:
    """Din99o Lch to lab."""

    l, c, h = lch
    h = util.no_nan(h)

    # If, for whatever reason (mainly direct user input),
    # if chroma is less than zero, clamp to zero.
    if c < 0.0:
        c = 0.0

    return [
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    ]


def lab_to_lch(lab: Vector) -> MutableVector:
    """Din99o Lab to Lch."""

    l, a, b = lab
    h = math.degrees(math.atan2(b, a))
    c = math.sqrt(a ** 2 + b ** 2)

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c <= ACHROMATIC_THRESHOLD:
        h = util.NaN

    return [l, c, util.constrain_hue(h)]


class Din99oLch(LchBase):
    """Lch D65 class."""

    BASE = 'din99o'
    SPACE = "din99o-lch"
    SERIALIZE = ("--din99o-lch",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    @classmethod
    def to_base(cls, lch: Vector) -> MutableVector:
        """To Lab."""

        return lch_to_lab(lch)

    @classmethod
    def from_base(cls, lab: Vector) -> MutableVector:
        """To Lab."""

        return lab_to_lch(lab)
