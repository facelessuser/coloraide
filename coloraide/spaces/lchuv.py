"""LChuv class."""
from __future__ import annotations
from ..spaces import Space
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .lch import LCh, ACHROMATIC_THRESHOLD, ACHROMATIC_HUE
from .. import util
import math
from .. import algebra as alg
from ..types import Vector


def luv_to_lchuv(luv: Vector) -> Vector:
    """Luv to LChuv."""

    l, u, v = luv

    c = math.sqrt(u ** 2 + v ** 2)
    h = math.degrees(math.atan2(v, u))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = alg.NaN

    return [l, c, util.constrain_hue(h)]


def lchuv_to_luv(lchuv: Vector) -> Vector:
    """LChuv to Luv."""

    l, c, h = lchuv

    # For better round tripping of achromatic colors,
    # use the achromatic hue that occurs in forward transform.
    # We use the one from white translation. It may vary slightly
    # depending on the grayscale color, but only slightly,
    # so this is close enough.
    if c < ACHROMATIC_THRESHOLD:
        h = ACHROMATIC_HUE

    if alg.is_nan(h):  # pragma: no cover
        return [l, 0.0, 0.0]

    return [
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    ]


class LChuv(LCh, Space):
    """LChuv class."""

    BASE = "luv"
    NAME = "lchuv"
    SERIALIZE = ("--lchuv",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("c", 0.0, 220.0, limit=(0.0, None)),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )

    def achromatic_hue(self) -> float:
        """Ideal achromatic hue."""

        return ACHROMATIC_HUE

    def to_base(self, coords: Vector) -> Vector:
        """To Luv from LChuv."""

        return lchuv_to_luv(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From Luv to LChuv."""

        return luv_to_lchuv(coords)
