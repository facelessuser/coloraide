"""
ACEScct color space.

https://www.oscars.org/science-technology/aces/aces-documentation
"""
from __future__ import annotations
import math
from ..channels import Channel
from ..spaces.srgb import sRGB
from ..types import Vector
from .acescc import CC_MAX

CCT_MIN = 0.0729055341958355
CCT_MAX = CC_MAX
C1 = 0.0078125
C2 = 10.5402377416545
C3 = 0.155251141552511


def acescct_to_acescg(acescc: Vector) -> Vector:
    """Convert ACEScc to ACEScg."""

    acescg = []
    for c in acescc:
        if c <= C3:
            c = (c - CCT_MIN) / C2
        elif C3 <= c < CCT_MAX:
            c = 2 ** (c * 17.52 - 9.72)
        else:
            c = 65504
        acescg.append(c)
    return acescg


def acescg_to_acescct(acescg: Vector) -> Vector:
    """Convert ACEScg to ACEScc."""

    acescc = []
    for c in acescg:
        if c <= C1:
            c = C2 * c + CCT_MIN
        elif c > C1:
            c = (math.log2(c) + 9.72) / 17.52
        acescc.append(c)
    return acescc


class ACEScct(sRGB):
    """The ACEScct color class."""

    BASE = "acescg"
    NAME = "acescct"
    SERIALIZE = ("--acescct",)  # type: tuple[str, ...]
    WHITE = (0.32168, 0.33767)
    CHANNELS = (
        Channel("r", CCT_MIN, CCT_MAX, bound=True),
        Channel("g", CCT_MIN, CCT_MAX, bound=True),
        Channel("b", CCT_MIN, CCT_MAX, bound=True)
    )
    DYNAMIC_RANGE = 'hdr'

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return acescct_to_acescg(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return acescg_to_acescct(coords)
