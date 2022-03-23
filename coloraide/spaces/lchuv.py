"""LCH class."""
from ..spaces import Space
from ..cat import WHITES
from ..gamut.bounds import GamutUnbound, FLG_ANGLE, FLG_OPT_PERCENT
from .lch import Lch, ACHROMATIC_THRESHOLD
from .. import util
import math
from ..util import MutableVector


def luv_to_lchuv(luv: MutableVector) -> MutableVector:
    """Luv to Lch(uv)."""

    l, u, v = luv

    c = math.sqrt(u ** 2 + v ** 2)
    h = math.degrees(math.atan2(v, u))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = util.NaN

    return [l, c, util.constrain_hue(h)]


def lchuv_to_luv(lchuv: MutableVector) -> MutableVector:
    """Lch(uv) to Luv."""

    l, c, h = lchuv
    if util.is_nan(h):  # pragma: no cover
        return [l, 0.0, 0.0]

    return [
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    ]


class Lchuv(Lch, Space):
    """Lch(uv) class."""

    BASE = "luv"
    NAME = "lchuv"
    SERIALIZE = ("--lchuv",)
    WHITE = WHITES['2deg']['D65']

    BOUNDS = (
        GamutUnbound(0, 100.0, FLG_OPT_PERCENT),
        GamutUnbound(0.0, 176.0),
        GamutUnbound(0.0, 360.0, FLG_ANGLE)
    )

    @classmethod
    def to_base(cls, coords: MutableVector) -> MutableVector:
        """To Luv from Lch(uv)."""

        return lchuv_to_luv(coords)

    @classmethod
    def from_base(cls, coords: MutableVector) -> MutableVector:
        """From Luv to Lch(uv)."""

        return luv_to_lchuv(coords)
