"""Lch class."""
from ...spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, Lchish, FLG_ANGLE, FLG_PERCENT
from ..lab.base import Lab
from ... import util
import re
import math
from ...util import Vector, MutableVector
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color

ACHROMATIC_THRESHOLD = 0.0000000002


def lab_to_lch(lab: Vector) -> MutableVector:
    """Lab to Lch."""

    l, a, b = lab

    c = math.sqrt(a ** 2 + b ** 2)
    h = math.degrees(math.atan2(b, a))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = util.NaN

    test = [l, c, util.constrain_hue(h)]
    return test


def lch_to_lab(lch: Vector) -> MutableVector:
    """Lch to Lab."""

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


class LchBase(Lchish, Space):
    """Lch class."""

    CHANNEL_NAMES = ("l", "c", "h", "alpha")
    CHANNEL_ALIASES = {
        "lightness": "l",
        "chroma": "c",
        "hue": "h"
    }

    BOUNDS = (
        # I think chroma, specifically should be clamped.
        # Some libraries don't to prevent rounding issues. We should only get
        # negative chroma via direct user input, but when translating to
        # Lab, this will be corrected.
        GamutUnbound(0.0, 100.0, FLG_PERCENT),
        GamutUnbound(0.0, 100.0),
        GamutUnbound(0.0, 360.0, FLG_ANGLE)
    )

    @property
    def l(self) -> float:
        """Lightness."""

        return self._coords[0]

    @l.setter
    def l(self, value: float) -> None:
        """Get true luminance."""

        self._coords[0] = self._handle_input(value)

    @property
    def c(self) -> float:
        """Chroma."""

        return self._coords[1]

    @c.setter
    def c(self, value: float) -> None:
        """chroma."""

        self._coords[1] = self._handle_input(value)

    @property
    def h(self) -> float:
        """Hue."""

        return self._coords[2]

    @h.setter
    def h(self, value: float) -> None:
        """Shift the hue."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def null_adjust(cls, coords: MutableVector, alpha: float) -> Tuple[MutableVector, float]:
        """On color update."""

        if coords[1] < ACHROMATIC_THRESHOLD:
            coords[2] = util.NaN
        return coords, alpha


class Lch(LchBase):
    """Lch class."""

    SPACE = "lch"
    SERIALIZE = ("--lch",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D50"

    @classmethod
    def _to_lab(cls, parent: 'Color', lch: Vector) -> MutableVector:
        """To Lab."""

        return lch_to_lab(lch)

    @classmethod
    def _from_lab(cls, parent: 'Color', lab: Vector) -> MutableVector:
        """To Lab."""

        return lab_to_lch(lab)

    @classmethod
    def _to_xyz(cls, parent: 'Color', lch: Vector) -> MutableVector:
        """To XYZ."""

        return Lab._to_xyz(parent, cls._to_lab(parent, lch))

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """From XYZ."""

        return cls._from_lab(parent, Lab._from_xyz(parent, xyz))
