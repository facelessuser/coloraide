"""LCH class."""
from ..spaces import Space
from ..cat import WHITES
from ..gamut.bounds import GamutUnbound, FLG_ANGLE, FLG_OPT_PERCENT
from .lch import Lch, ACHROMATIC_THRESHOLD
from .. import util
import math
from .. import algebra as alg
from ..types import Vector


def luv_to_lchuv(luv: Vector) -> Vector:
    """Luv to Lch(uv)."""

    l, u, v = luv

    c = math.sqrt(u ** 2 + v ** 2)
    h = math.degrees(math.atan2(v, u))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = alg.NaN

    return [l, c, util.constrain_hue(h)]


def lchuv_to_luv(lchuv: Vector) -> Vector:
    """Lch(uv) to Luv."""

    l, c, h = lchuv
    if alg.is_nan(h):  # pragma: no cover
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
    def to_base(cls, coords: Vector) -> Vector:
        """To Luv from Lch(uv)."""

        return lchuv_to_luv(coords)

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From Luv to Lch(uv)."""

        return luv_to_lchuv(coords)
