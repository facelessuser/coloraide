"""
Prismatic color space.

Creates a Maxwell color triangle with a lightness component.

http://psgraphics.blogspot.com/2015/10/prismatic-color-model.html
https://studylib.net/doc/14656976/the-prismatic-color-space-for-rgb-computations
"""
from __future__ import annotations
from ..spaces import Space
from ..channels import Channel
from ..cat import WHITES
from ..types import Vector
from .. import algebra as alg
import math


def srgb_to_lrgb(rgb: Vector) -> Vector:
    """Convert sRGB to Prismatic."""

    l = max(rgb)
    s = sum(rgb)
    return [l] + ([(c / s) for c in rgb] if s != 0 else [0, 0, 0])


def lrgb_to_srgb(lrgb: Vector) -> Vector:
    """Convert Prismatic to sRGB."""

    rgb = lrgb[1:]
    l = lrgb[0]
    mx = max(rgb)
    return [(l * c) / mx for c in rgb] if mx != 0 else [0, 0, 0]


class Prismatic(Space):
    """The Prismatic color class."""

    BASE = "srgb"
    NAME = "prismatic"
    SERIALIZE = ("--prismatic",)  # type: tuple[str, ...]
    EXTENDED_RANGE = False
    CHANNELS = (
        Channel("l", 0.0, 1.0, bound=True),
        Channel("r", 0.0, 1.0, bound=True),
        Channel("g", 0.0, 1.0, bound=True),
        Channel("b", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "lightness": 'l',
        "red": 'r',
        "green": 'g',
        "blue": 'b'
    }
    WHITE = WHITES['2deg']['D65']

    def is_achromatic(self, coords: Vector) -> bool:
        """Test if color is achromatic."""

        if math.isclose(0.0, coords[0], abs_tol=1e-4):
            return True

        white = [1, 1, 1]
        for x in alg.vcross(coords[:-1], white):
            if not math.isclose(0.0, x, abs_tol=1e-5):
                return False
        return True

    def to_base(self, coords: Vector) -> Vector:
        """To sRGB."""

        return lrgb_to_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From sRGB."""

        return srgb_to_lrgb(coords)
