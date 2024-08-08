"""HSV class."""
from __future__ import annotations
from ..spaces import Space, HSVish
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .. import util
from ..types import Vector


def hsv_to_srgb(hsv: Vector) -> Vector:
    """
    Convert HSV to sRGB.

    https://en.wikipedia.org/wiki/HSL_and_HSV#HSV_to_RGB_alternative
    """

    h, s, v = hsv
    h = util.constrain_hue(h) / 60

    def f(n: int) -> float:
        """Calculate the channels."""

        k = (n + h) % 6
        return v - v * s * max(0, min([k, 4 - k, 1]))

    return [f(5), f(3), f(1)]


def srgb_to_hsv(rgb: Vector) -> Vector:
    """
    Convert sRGB to HSV.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Hue_and_chroma
    https://en.wikipedia.org/wiki/HSL_and_HSV#Saturation
    https://en.wikipedia.org/wiki/HSL_and_HSV#Lightness
    """

    r, g, b = rgb
    v = max(rgb)
    mn = min(rgb)
    h = 0.0
    s = 0.0
    c = v - mn

    if c != 0.0:
        if v == r:
            h = (g - b) / c
        elif v == g:
            h = (b - r) / c + 2.0
        else:
            h = (r - g) / c + 4.0
        h *= 60.0

    if v:
        s = c / v

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
