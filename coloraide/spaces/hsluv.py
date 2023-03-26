"""
HSLuv color space.

Adapted to Python and ColorAide by Isaac Muse (2021)

--- HSLuv Conversion Algorithm ---
Copyright (c) 2012-2021 Alexei Boronine
Copyright (c) 2016 Florian Dormont

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations
from ..spaces import Space, HSLish
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .lab import EPSILON, KAPPA
from .srgb_linear import XYZ_TO_RGB
import math
from .. import util
from ..types import Vector


def length_of_ray_until_intersect(theta: float, line: dict[str, float]) -> float:
    """Length of ray until intersect."""

    return line['intercept'] / (math.sin(theta) - line['slope'] * math.cos(theta))


def get_bounds(l: float) -> list[dict[str, float]]:
    """Get bounds."""

    result = []
    sub1 = ((l + 16) ** 3) / 1560896
    sub2 = sub1 if sub1 > EPSILON else l / KAPPA

    g = 0
    while g < 3:
        c = g
        g += 1
        m1, m2, m3 = XYZ_TO_RGB[c]
        g1 = 0
        while g1 < 2:
            t = g1
            g1 += 1
            top1 = (284517 * m1 - 94839 * m3) * sub2
            top2 = (838422 * m3 + 769860 * m2 + 731718 * m1) * l * sub2 - (769860 * t) * l
            bottom = (632260 * m3 - 126452 * m2) * sub2 + 126452 * t
            result.append({'slope': top1 / bottom, 'intercept': top2 / bottom})
    return result


def max_chroma_for_lh(l: float, h: float) -> float:
    """Get max from for l * h."""

    hrad = math.radians(h)
    lengths = [length_of_ray_until_intersect(hrad, bound) for bound in get_bounds(l)]
    return min(length for length in lengths if length >= 0)


def hsluv_to_lch(hsluv: Vector) -> Vector:
    """Convert HSLuv to LCh."""

    h, s, l = hsluv
    c = 0.0
    if l > 100 - 1e-7:
        l = 100.0
    elif l < 1e-08:
        l = 0.0
    else:
        _hx_max = max_chroma_for_lh(l, h)
        c = _hx_max / 100.0 * s
    return [l, c, util.constrain_hue(h)]


def lch_to_hsluv(lch: Vector) -> Vector:
    """Convert LCh to HSLuv."""

    l, c, h = lch
    s = 0.0
    if l > 100 - 1e-7:
        l = 100.0
    elif l < 1e-08:
        l = 0.0
    else:
        _hx_max = max_chroma_for_lh(l, h)
        s = c / _hx_max * 100.0
    return [util.constrain_hue(h), s, l]


class HSLuv(HSLish, Space):
    """HSLuv class."""

    BASE = 'lchuv'
    NAME = "hsluv"
    SERIALIZE = ("--hsluv",)
    CHANNELS = (
        Channel("h", 0.0, 360.0, bound=True, flags=FLG_ANGLE),
        Channel("s", 0.0, 100.0, bound=True),
        Channel("l", 0.0, 100.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "lightness": "l"
    }
    WHITE = WHITES['2deg']['D65']
    GAMUT_CHECK = "srgb"

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return abs(coords[1]) < 1e-4 or coords[2] > (100 - 1e-7) or coords[2] < 1e-08

    def to_base(self, coords: Vector) -> Vector:
        """To LChuv from HSLuv."""

        return hsluv_to_lch(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From LChuv to HSLuv."""

        return lch_to_hsluv(coords)
