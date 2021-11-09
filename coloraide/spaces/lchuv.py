"""LCH class."""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, Lchish, FLG_ANGLE, FLG_PERCENT
from .luv import Luv
from .. import util
import re
import math
from ..util import Vector, MutableVector
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

ACHROMATIC_THRESHOLD = 0.0000000002


def luv_to_lchuv(luv: Vector) -> MutableVector:
    """Luv to Lch(uv)."""

    l, u, v = luv

    c = math.sqrt(u ** 2 + v ** 2)
    h = math.degrees(math.atan2(v, u))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = util.NaN

    return [l, c, util.constrain_hue(h)]


def lchuv_to_luv(lchuv: Vector) -> MutableVector:
    """Lch(uv) to Luv."""

    l, c, h = lchuv
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


class Lchuv(Lchish, Space):
    """Lch(uv) class."""

    SPACE = "lchuv"
    SERIALIZE = ("--lchuv",)
    CHANNEL_NAMES = ("l", "c", "h", "alpha")
    CHANNEL_ALIASES = {
        "lightness": "l",
        "chroma": "c",
        "hue": "h"
    }
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D50"

    BOUNDS = (
        GamutUnbound(0, 100.0, FLG_PERCENT),
        GamutUnbound(0.0, 176.0),
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

    @classmethod
    def _to_luv(cls, parent: 'Color', lchuv: Vector) -> MutableVector:
        """To Luv."""

        return lchuv_to_luv(lchuv)

    @classmethod
    def _from_luv(cls, parent: 'Color', luv: Vector) -> MutableVector:
        """To Luv."""

        return luv_to_lchuv(luv)

    @classmethod
    def _to_xyz(cls, parent: 'Color', lchuv: Vector) -> MutableVector:
        """To XYZ."""

        return Luv._to_xyz(parent, cls._to_luv(parent, lchuv))

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """From XYZ."""

        return cls._from_luv(parent, Luv._from_xyz(parent, xyz))
