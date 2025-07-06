"""
XYB color space.

https://ds.jpeg.org/whitepapers/jpeg-xl-whitepaper.pdf
"""
from __future__ import annotations
from .. import algebra as alg
from ..spaces.lab import Lab
from ..types import Vector
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT

BIAS = 0.00379307325527544933
BIAS_CBRT = alg.nth_root(BIAS, 3)

LRGB_TO_LMS = [
    [0.3, 0.622, 0.078],
    [0.23, 0.692, 0.078],
    [0.24342268924547819, 0.20476744424496821, 0.55180986650955360]
]

LMS_TO_LRGB = [
    [11.031566904639865, -9.866943908131564, -0.16462299650829934],
    [-3.254147381074425, 4.4187703775827245, -0.16462299650829929],
    [-3.6588512867136815, 2.712923045936092, 1.945928240777589]
]

XYB_LMS_TO_XYB = [
    [0.5, -0.5, 0.0],
    [0.5, 0.5, 0.0],
    [0.0, 0.0, 1.0]
]

XYB_TO_XYB_LMS = [
    [1.0, 1.0, 0.0],
    [-1.0, 1.0, 0.0],
    [0.0, 0.0, 1.0]
]


def rgb_to_xyb(rgb: Vector) -> Vector:
    """Linear sRGB to XYB."""

    xyb = alg.matmul_x3(
        XYB_LMS_TO_XYB,
        [alg.nth_root(c + BIAS, 3) - BIAS_CBRT for c in alg.matmul_x3(LRGB_TO_LMS, rgb, dims=alg.D2_D1)],
        dims=alg.D2_D1
    )

    # https://twitter.com/jonsneyers/status/1605321352143331328
    # @jonsneyers Feb 22
    # Yes, the default is to just subtract Y from B. In general there are locally
    # signaled float multipliers to subtract some multiple of Y from X and some
    # other multiple from B. But this is the baseline, making X=B=0 grayscale.
    xyb[2] -= xyb[1]
    return xyb


def xyb_to_rgb(xyb: Vector) -> Vector:
    """XYB to linear sRGB."""

    # This cleans up the round trip on black.
    if not any(xyb):
        return [0.0] * 3

    xyb[2] += xyb[1]
    return alg.matmul_x3(
        LMS_TO_LRGB,
        [(c + BIAS_CBRT) ** 3 - BIAS for c in alg.matmul_x3(XYB_TO_XYB_LMS, xyb, dims=alg.D2_D1)],
        dims=alg.D2_D1
    )


class XYB(Lab):
    """XYB color class."""

    BASE = 'srgb-linear'
    NAME = "xyb"
    SERIALIZE = ("--xyb",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("x", -0.05, 0.05, flags=FLG_MIRROR_PERCENT),
        Channel("y", 0.0, 0.845),
        Channel("b", -0.45, 0.45, flags=FLG_MIRROR_PERCENT)
    )

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return alg.rect_to_polar(coords[0], coords[2])[0] < self.achromatic_threshold

    def names(self) -> tuple[Channel, ...]:
        """Return Lab-ish names in the order L a b."""

        channels = self.channels
        return channels[1], channels[0], channels[2]

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "y"

    def to_base(self, coords: Vector) -> Vector:
        """To XYB from base."""

        return xyb_to_rgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From base to XYB."""

        return rgb_to_xyb(coords)
