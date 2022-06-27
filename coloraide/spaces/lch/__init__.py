"""Lch class."""
from ...spaces import Space, Lchish
from ...cat import WHITES
from ...gamut.bounds import GamutUnbound, FLG_ANGLE, FLG_OPT_PERCENT
from ... import util
import math
from ... import algebra as alg
from ...types import Vector
from typing import Tuple

ACHROMATIC_THRESHOLD = 0.0000000002


def lab_to_lch(lab: Vector) -> Vector:
    """Lab to Lch."""

    l, a, b = lab

    c = math.sqrt(a ** 2 + b ** 2)
    h = math.degrees(math.atan2(b, a))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = alg.NaN

    return [l, c, util.constrain_hue(h)]


def lch_to_lab(lch: Vector) -> Vector:
    """Lch to Lab."""

    l, c, h = lch
    if alg.is_nan(h):  # pragma: no cover
        return [l, 0.0, 0.0]

    return [
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    ]


class Lch(Lchish, Space):
    """Lch class."""

    BASE = "lab"
    NAME = "lch"
    SERIALIZE = ("--lch",)
    CHANNEL_NAMES = ("l", "c", "h")
    CHANNEL_ALIASES = {
        "lightness": "l",
        "chroma": "c",
        "hue": "h"
    }
    WHITE = WHITES['2deg']['D50']
    BOUNDS = (
        GamutUnbound(0.0, 100.0, FLG_OPT_PERCENT),
        GamutUnbound(0.0, 100.0),
        GamutUnbound(0.0, 360.0, FLG_ANGLE)
    )

    @classmethod
    def l(self, value: float) -> float:
        """Get true luminance."""

        return value

    @classmethod
    def c(self, value: float) -> float:
        """chroma."""

        return alg.clamp(value, 0.0)

    @classmethod
    def h(self, value: float) -> float:
        """Shift the hue."""

        return value

    @classmethod
    def null_adjust(cls, coords: Vector, alpha: float) -> Tuple[Vector, float]:
        """On color update."""

        coords = alg.no_nans(coords)
        if coords[1] < ACHROMATIC_THRESHOLD:
            coords[2] = alg.NaN
        return coords, alg.no_nan(alpha)

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To Lab from Lch."""

        return lch_to_lab(coords)

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From Lab to Lch."""

        return lab_to_lch(coords)
