"""
oRGB color space.

https://graphics.stanford.edu/~boulos/papers/orgb_sig.pdf
"""
from __future__ import annotations
import math
from .. import algebra as alg
from ..spaces import Space, Labish
from ..types import Vector
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT

RGB_TO_LC1C2 = [
    [0.2990, 0.5870, 0.1140],
    [0.5000, 0.5000, -1.0000],
    [0.8660, -0.8660, 0.0000]
]

LC1C2_TO_RGB = alg.inv(RGB_TO_LC1C2)


def rotate(v: Vector, d: float) -> Vector:
    """Rotate the vector."""

    m = alg.identity(3)
    m[1][1:] = math.cos(d), -math.sin(d)
    m[2][1:] = math.sin(d), math.cos(d)
    return alg.dot(m, v, dims=alg.D2_D1)


def srgb_to_orgb(rgb: Vector) -> Vector:
    """sRGB to oRGB."""

    lcc = alg.dot(RGB_TO_LC1C2, rgb, dims=alg.D2_D1)
    theta = math.atan2(lcc[2], lcc[1])
    theta0 = theta
    atheta = abs(theta)
    if atheta < (math.pi / 3):
        theta0 = (3 / 2) * theta
    elif (math.pi / 3) <= atheta <= math.pi:
        theta0 = math.copysign((math.pi / 2) + (3 / 4) * (atheta - math.pi / 3), theta)

    return rotate(lcc, theta0 - theta)


def orgb_to_srgb(lcc: Vector) -> Vector:
    """oRGB to sRGB."""

    theta0 = math.atan2(lcc[2], lcc[1])
    theta = theta0
    atheta0 = abs(theta0)
    if atheta0 < (math.pi / 2):
        theta = (2 / 3) * theta0
    elif (math.pi / 2) <= atheta0 <= math.pi:
        theta = math.copysign((math.pi / 3) + (4 / 3) * (atheta0 - math.pi / 2), theta0)

    return alg.dot(LC1C2_TO_RGB, rotate(lcc, theta - theta0), dims=alg.D2_D1)


class oRGB(Labish, Space):
    """oRGB color class."""

    BASE = 'srgb'
    NAME = "orgb"
    SERIALIZE = ("--orgb",)
    WHITE = WHITES['2deg']['D65']
    EXTENDED_RANGE = True
    CHANNELS = (
        Channel("l", 0.0, 1.0, bound=True),
        Channel("cyb", -1.0, 1.0, bound=True, flags=FLG_MIRROR_PERCENT),
        Channel("crg", -1.0, 1.0, bound=True, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "luma": "l"
    }

    def names(self) -> tuple[str, ...]:
        """
        Return Lab-ish names in the order L a b.

        oRGB flips the `crg` and `cyb` equivalent (which corresponds to `a` and `b`).
        """

        channels = self.channels
        return channels[0], channels[2], channels[1]

    def to_base(self, coords: Vector) -> Vector:
        """To base from oRGB."""

        return orgb_to_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From base to oRGB."""

        return srgb_to_orgb(coords)
