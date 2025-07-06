"""
Uncalibrated, naive CMYK color space.

https://www.w3.org/TR/css-color-5/#cmyk-rgb
"""
from __future__ import annotations
from .. import util
from ..spaces import Space
from ..channels import Channel
from ..cat import WHITES
from ..types import Vector
from .. import algebra as alg
import math


def srgb_to_cmyk(cmy: Vector) -> Vector:
    """Convert sRGB to CMYK."""

    k = min(cmy)
    if k == 1:
        return [0.0, 0.0, 0.0, k]
    cmyk = [(v - k) / (1.0 - k) for v in cmy]
    cmyk.append(k)
    return cmyk


def cmyk_to_srgb(cmyk: Vector) -> Vector:
    """Convert CMYK to sRGB."""

    k = cmyk[-1]
    return [v * (1.0 - k) + k for v in cmyk[:-1]]


class CMYK(Space):
    """The CMYK color class."""

    BASE = "cmy"
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
    SUBTRACTIVE = True
    GAMUT_CHECK = 'cmy'
    CLIP_SPACE = 'cmyk'

    def is_achromatic(self, coords: Vector) -> bool:
        """Test if color is achromatic."""

        if math.isclose(1.0, coords[-1], abs_tol=util.ACHROMATIC_THRESHOLD_SM):
            return True

        black = [1, 1, 1]
        for x in alg.vcross(coords[:-1], black):
            if not math.isclose(0.0, x, abs_tol=util.ACHROMATIC_THRESHOLD_SM):
                return False
        return True

    def to_base(self, coords: Vector) -> Vector:
        """To sRGB."""

        return cmyk_to_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From sRGB."""

        return srgb_to_cmyk(coords)
