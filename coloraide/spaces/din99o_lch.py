"""Din99o Lch class."""
from ..spaces import RE_DEFAULT_MATCH
from .lch.base import LchBase
from .din99o import Din99o
from .. import util
import math
import re
from ..util import Vector, MutableVector
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

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

    SPACE = "din99o-lch"
    SERIALIZE = ("--din99o-lch",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    @classmethod
    def _to_din99o(cls, parent: 'Color', lch: Vector) -> MutableVector:
        """To Lab."""

        return lch_to_lab(lch)

    @classmethod
    def _from_din99o(cls, parent: 'Color', lab: Vector) -> MutableVector:
        """To Lab."""

        return lab_to_lch(lab)

    @classmethod
    def _to_xyz(cls, parent: 'Color', lch: Vector) -> MutableVector:
        """To XYZ."""

        return Din99o._to_xyz(parent, cls._to_din99o(parent, lch))

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """From XYZ."""

        return cls._from_din99o(parent, Din99o._from_xyz(parent, xyz))
