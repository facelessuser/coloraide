"""Uncalibrated, naive CMY color space."""
from __future__ import annotations
from ..spaces import Space
from ..channels import Channel
from ..cat import WHITES
from ..types import Vector
from .. import algebra as alg
import math


def srgb_to_cmy(rgb: Vector) -> Vector:
    """Convert sRGB to CMY."""

    return [1 - c for c in rgb]


def cmy_to_srgb(cmy: Vector) -> Vector:
    """Convert CMY to sRGB."""

    return [1 - c for c in cmy]


class CMY(Space):
    """The CMY color class."""

    BASE = "srgb"
    NAME = "cmy"
    SERIALIZE = ("--cmy",)  # type: tuple[str, ...]
    CHANNELS = (
        Channel("c", 0.0, 1.0, bound=True),
        Channel("m", 0.0, 1.0, bound=True),
        Channel("y", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "cyan": 'c',
        "magenta": 'm',
        "yellow": 'y'
    }
    WHITE = WHITES['2deg']['D65']

    def is_achromatic(self, coords: Vector) -> bool:
        """Test if color is achromatic."""

        black = [1, 1, 1]
        for x in alg.vcross(coords, black):
            if not math.isclose(0.0, x, abs_tol=1e-4):
                return False
        return True

    def to_base(self, coords: Vector) -> Vector:
        """To sRGB."""

        return cmy_to_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From sRGB."""

        return srgb_to_cmy(coords)
