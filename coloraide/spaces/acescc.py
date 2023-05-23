"""
ACEScc color space.

https://www.oscars.org/science-technology/aces/aces-documentation
"""
from __future__ import annotations
import math
from ..channels import Channel
from ..spaces.srgb import sRGB
from ..types import Vector

CC_MIN = (math.log2(2 ** -16) + 9.72) / 17.52
CC_MAX = (math.log2(65504) + 9.72) / 17.52


def acescc_to_acescg(acescc: Vector) -> Vector:
    """Convert ACEScc to XYZ."""

    c1 = 2 ** -16
    c2 = (9.72 - 15) / 17.52
    c3 = (math.log2(65504) + 9.72) / 17.52

    acescg = []
    for c in acescc:
        if c <= c2:
            c = (2 ** (c * 17.52 - 9.72) - c1) * 2.0
        elif c2 <= c < c3:
            c = 2 ** (c * 17.52 - 9.72)
        else:
            c = 65504.0
        acescg.append(c)
    return acescg


def acescg_to_acescc(acescg: Vector) -> Vector:
    """Convert XYZ to ACEScc."""

    c1 = 2 ** -16
    c2 = 2 ** -15

    acescc = []
    for c in acescg:
        if c <= 0:
            c = math.log2(c1)
        elif c < c2:
            c = math.log2(c1 + c * 0.5)
        else:
            c = math.log2(c)
        acescc.append((c + 9.72) / 17.52)
    return acescc


class ACEScc(sRGB):
    """The ACEScc color class."""

    BASE = "acescg"
    NAME = "acescc"
    SERIALIZE = ("--acescc",)  # type: tuple[str, ...]
    WHITE = (0.32168, 0.33767)
    CHANNELS = (
        Channel("r", CC_MIN, CC_MAX, bound=True, nans=CC_MIN),
        Channel("g", CC_MIN, CC_MAX, bound=True, nans=CC_MIN),
        Channel("b", CC_MIN, CC_MAX, bound=True, nans=CC_MIN)
    )
    DYNAMIC_RANGE = 'hdr'

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return acescc_to_acescg(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return acescg_to_acescc(coords)
