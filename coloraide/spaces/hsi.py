"""
HSI class.

https://en.wikipedia.org/wiki/HSL_and_HSV#Saturation
"""
from __future__ import annotations
from ..spaces import Space, Cylindrical
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .. import algebra as alg
from .. import util
from ..types import Vector


def srgb_to_hsi(rgb: Vector) -> Vector:
    """sRGB to HSI."""

    r, g, b = rgb
    h = alg.NaN
    s = 0.0
    mx = max(rgb)
    mn = min(rgb)
    i = sum(rgb) * 1 / 3
    s = 0 if (-1e-08 < i <= 0.0) else 1 - (mn / i)
    c = mx - mn

    if c != 0.0:
        if mx == r:
            h = (g - b) / c
        elif mx == g:
            h = (b - r) / c + 2.0
        else:
            h = (r - g) / c + 4.0
        h *= 60.0

    if abs(s) < 1e-08:
        h = alg.NaN

    return [util.constrain_hue(h), s, i]


def hsi_to_srgb(hsi: Vector) -> Vector:
    """HSI to RGB."""

    h, s, i = hsi
    h = util.constrain_hue(h)
    h /= 60
    z = 1 - abs(h % 2 - 1)
    c = (3 * i * s) / (1 + z)
    x = c * z

    if alg.is_nan(h):  # pragma: no cover
        # In our current setup, this will not occur. If colors are naturally achromatic,
        # they will resolve to zeros automatically even without this check. This case
        # would be a shortcut normally.
        #
        # Unnatural cases, such as explicitly setting of hue to undefined, could cause this,
        # but the conversion pipeline converts all undefined values to zero. We'd have to
        # encounter a natural case due to conversion to or from HSI mid pipeline to trigger
        # this, and we are not currently in a position where that would occur with sRGB being
        # the only pass-through.
        rgb = [0.0] * 3
    elif 0 <= h <= 1:
        rgb = [c, x, 0]
    elif 1 <= h <= 2:
        rgb = [x, c, 0]
    elif 2 <= h <= 3:
        rgb = [0, c, x]
    elif 3 <= h <= 4:
        rgb = [0, x, c]
    elif 4 <= h <= 5:
        rgb = [x, 0, c]
    else:
        rgb = [c, 0, x]
    m = i * (1 - s)

    return [chan + m for chan in rgb]


class HSI(Cylindrical, Space):
    """HSI class."""

    BASE = "srgb"
    NAME = "hsi"
    SERIALIZE = ("--hsi",)
    CHANNELS = (
        Channel("h", 0.0, 360.0, bound=True, flags=FLG_ANGLE),
        Channel("s", 0.0, 1.0, bound=True),
        Channel("i", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "intensity": "i"
    }
    WHITE = WHITES['2deg']['D65']
    GAMUT_CHECK = "srgb"

    def normalize(self, coords: Vector) -> Vector:
        """On color update."""

        h, s, i = alg.no_nans(coords[:-1])
        h = util.constrain_hue(h)
        h /= 60
        z = 1 - abs(h % 2 - 1)
        c = (3 * i * s) / (1 + z)

        if c == 0 or abs(s) < 1e-08:
            coords[0] = alg.NaN

        return coords

    def to_base(self, coords: Vector) -> Vector:
        """To sRGB from HSI."""

        return hsi_to_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From sRGB to HSI."""

        return srgb_to_hsi(coords)
