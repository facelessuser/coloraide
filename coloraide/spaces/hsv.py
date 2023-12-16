"""HSV class."""
from __future__ import annotations
from ..spaces import Space, HSVish
from .hsl import srgb_to_hsl, hsl_to_srgb
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .. import util
from ..types import Vector


def hsv_to_srgb(hsv: Vector) -> Vector:
    """
    HSV to HSL.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    h, s, v = hsv
    l = v * (1.0 - s / 2.0)
    s = 0.0 if l == 0.0 or l == 1.0 else (v - l) / min(l, 1.0 - l)

    return hsl_to_srgb([h, s, l])


def srgb_to_hsv(srgb: Vector) -> Vector:
    """
    HSL to HSV.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    h, s, l = srgb_to_hsl(srgb)
    v = l + s * min(l, 1.0 - l)
    s = 0.0 if v == 0.0 else 2 * (1.0 - l / v)

    return [util.constrain_hue(h), s, v]


class HSV(HSVish, Space):
    """HSL class."""

    BASE = "srgb"
    NAME = "hsv"
    SERIALIZE = ("--hsv",)
    CHANNELS = (
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE),
        Channel("s", 0.0, 1.0, bound=True),
        Channel("v", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "value": "v"
    }
    GAMUT_CHECK = "srgb"  # type: str | None
    CLIP_SPACE = "hsv"  # type: str | None
    WHITE = WHITES['2deg']['D65']

    def normalize(self, coords: Vector) -> Vector:
        """Normalize coordinates."""

        if coords[1] < 0:
            return self.from_base(self.to_base(coords))
        coords[0] %= 360.0
        return coords

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return abs(coords[1]) < 1e-5 or coords[2] == 0.0

    def to_base(self, coords: Vector) -> Vector:
        """To HSL from HSV."""

        return hsv_to_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From HSL to HSV."""

        return srgb_to_hsv(coords)
