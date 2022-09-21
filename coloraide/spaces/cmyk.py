"""
Uncalibrated, naive CMYK color space.

https://www.w3.org/TR/css-color-5/#cmyk-rgb
"""
from __future__ import annotations
from ..spaces import Space
from ..channels import Channel
from ..cat import WHITES
from ..types import Vector


def srgb_to_cmyk(rgb: Vector) -> Vector:
    """Convert sRGB to CMYK."""

    k = 1.0 - max(rgb)
    c = m = y = 0.0
    if k != 1:
        r, g, b = rgb
        c = (1.0 - r - k) / (1.0 - k)
        m = (1.0 - g - k) / (1.0 - k)
        y = (1.0 - b - k) / (1.0 - k)

    return [c, m, y, k]


def cmyk_to_srgb(cmyk: Vector) -> Vector:
    """Convert CMYK to sRGB."""

    c, m, y, k = cmyk
    return [
        1.0 - min(1.0, c * (1.0 - k) + k),
        1.0 - min(1.0, m * (1.0 - k) + k),
        1.0 - min(1.0, y * (1.0 - k) + k)
    ]


class CMYK(Space):
    """The CMYK color class."""

    BASE = "srgb"
    NAME = "cmyk"
    SERIALIZE = ("--cmyk",)  # type: tuple[str, ...]
    CHANNELS = (
        Channel("c", 0.0, 1.0, bound=True),
        Channel("m", 0.0, 1.0, bound=True),
        Channel("y", 0.0, 1.0, bound=True),
        Channel("k", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "cyan": 'c',
        "magenta": 'm',
        "yellow": 'y',
        "black": 'k'
    }
    WHITE = WHITES['2deg']['D65']

    def to_base(self, coords: Vector) -> Vector:
        """To sRGB."""

        return cmyk_to_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From sRGB."""

        return srgb_to_cmyk(coords)
