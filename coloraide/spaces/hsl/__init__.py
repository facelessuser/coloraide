"""HSL class."""
from ...spaces import Space, Cylindrical
from ...cat import WHITES
from ...gamut.bounds import GamutBound, FLG_ANGLE, FLG_PERCENT
from ... import util
from ... import algebra as alg
from ...types import Vector
from typing import Tuple


def srgb_to_hsl(rgb: Vector) -> Vector:
    """SRGB to HSL."""

    r, g, b = rgb
    mx = max(rgb)
    mn = min(rgb)
    h = alg.NaN
    s = 0.0
    l = (mn + mx) / 2
    c = mx - mn

    if c != 0.0:
        if mx == r:
            h = (g - b) / c
        elif mx == g:
            h = (b - r) / c + 2.0
        else:
            h = (r - g) / c + 4.0
        s = 0 if l == 0 or l == 1 else (mx - l) / min(l, 1 - l)
        h *= 60.0
        if s == 0:
            h = alg.NaN

    return [util.constrain_hue(h), s, l]


def hsl_to_srgb(hsl: Vector) -> Vector:
    """
    HSL to RGB.

    https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB_alternative
    """

    h, s, l = hsl
    h = h % 360

    def f(n: int) -> float:
        """Calculate the channels."""
        k = (n + h / 30) % 12
        a = s * min(l, 1 - l)
        return l - a * max(-1, min(k - 3, 9 - k, 1))

    return [f(0), f(8), f(4)]


class HSL(Cylindrical, Space):
    """HSL class."""

    BASE = "srgb"
    NAME = "hsl"
    SERIALIZE = ("--hsl",)
    CHANNEL_NAMES = ("h", "s", "l")
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "lightness": "l"
    }
    WHITE = WHITES['2deg']['D65']
    GAMUT_CHECK = "srgb"

    BOUNDS = (
        GamutBound(0.0, 360.0, FLG_ANGLE),
        GamutBound(0.0, 1.0, FLG_PERCENT),
        GamutBound(0.0, 1.0, FLG_PERCENT)
    )

    @property
    def h(self) -> float:
        """Hue channel."""

        return self._coords[0]

    @h.setter
    def h(self, value: float) -> None:
        """Shift the hue."""

        self._coords[0] = value

    @property
    def s(self) -> float:
        """Saturation channel."""

        return self._coords[1]

    @s.setter
    def s(self, value: float) -> None:
        """Saturate or unsaturate the color by the given factor."""

        self._coords[1] = value

    @property
    def l(self) -> float:
        """Lightness channel."""

        return self._coords[2]

    @l.setter
    def l(self, value: float) -> None:
        """Set lightness channel."""

        self._coords[2] = value

    @classmethod
    def null_adjust(cls, coords: Vector, alpha: float) -> Tuple[Vector, float]:
        """On color update."""

        coords = alg.no_nans(coords)
        if coords[1] == 0 or coords[2] in (0, 1):
            coords[0] = alg.NaN

        return coords, alg.no_nan(alpha)

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To sRGB from HSL."""

        return hsl_to_srgb(coords)

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From sRGB to HSL."""

        return srgb_to_hsl(coords)
