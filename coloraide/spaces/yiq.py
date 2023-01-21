"""YIQ color space."""
from __future__ import annotations
from .. import algebra as alg
from ..spaces import Space, Labish
from ..types import Vector
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT
from typing import cast

SRGB_TO_YIQ = [
    [0.29889531, 0.58662247, 0.11448223],
    [0.59597799, -0.27417610, -0.32180189],
    [0.21147017, -0.52261711, 0.31114694]
]

YIQ_TO_SRGB = alg.inv(SRGB_TO_YIQ)


def srgb_to_yiq(srgb: Vector) -> Vector:
    """Convert sRGB to YIQ."""

    return alg.dot(SRGB_TO_YIQ, srgb)


def yiq_to_srgb(yiq: Vector) -> Vector:
    """Convert YIQ to sRGB."""

    return alg.dot(YIQ_TO_SRGB, yiq)


class YIQ(Labish, Space):
    """YIQ color class."""

    BASE = 'srgb'
    NAME = "yiq"
    SERIALIZE = ("--yiq",)
    WHITE = WHITES['2deg']['D65']
    EXTENDED_RANGE = True
    CHANNELS = (
        Channel("y", 0.0, 1.0, bound=True),
        Channel("i", -0.59597799, 0.59597799, bound=True, flags=FLG_MIRROR_PERCENT),
        Channel("q", -0.52261711, 0.52261711, bound=True, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "luma": "y",
        "in-phase": "i",
        "quadrature": "q"
    }

    def labish_names(self) -> tuple[str, ...]:
        """Return Lab-ish names in the order L a b."""

        channels = cast(Space, self).channels
        return channels[0], channels[2], channels[1]

    def to_base(self, coords: Vector) -> Vector:
        """To base from YIQ."""

        return yiq_to_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From base to YIQ."""

        return srgb_to_yiq(coords)
