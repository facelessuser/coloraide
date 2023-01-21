"""YUV color space."""
from __future__ import annotations
import math
from .. import algebra as alg
from ..spaces import Space, Labish
from ..types import Vector
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT
from typing import cast

RAD_33 = math.radians(33)

YUV_TO_YIQ = [
    [1.0, 0.0, 0.0],
    [0.0, -math.sin(RAD_33), math.cos(RAD_33)],
    [0.0, math.cos(RAD_33), math.sin(RAD_33)]
]

YIQ_TO_YUV = YUV_TO_YIQ


def yiq_to_yuv(srgb: Vector) -> Vector:
    """Convert YIQ to YUV."""

    return alg.dot(YIQ_TO_YUV, srgb)


def yuv_to_yiq(yiq: Vector) -> Vector:
    """Convert YUV to YIQ."""

    return alg.dot(YUV_TO_YIQ, yiq)


class YUV(Labish, Space):
    """YUV color class."""

    BASE = 'yiq'
    NAME = "yuv"
    SERIALIZE = ("--yuv",)
    WHITE = WHITES['2deg']['D65']
    EXTENDED_RANGE = True
    CHANNELS = (
        Channel("y", 0.0, 1.0, bound=True),
        Channel("u", -0.43621565, 0.43621565, bound=True, flags=FLG_MIRROR_PERCENT),
        Channel("v", -0.61500411, 0.61500411, bound=True, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "luma": "y"
    }

    def labish_names(self) -> tuple[str, ...]:
        """Return Lab-ish names in the order L a b."""

        channels = cast(Space, self).channels
        return channels[0], channels[2], channels[1]

    def to_base(self, coords: Vector) -> Vector:
        """To base from YUV."""

        return yuv_to_yiq(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From base to YUV."""

        return yiq_to_yuv(coords)
