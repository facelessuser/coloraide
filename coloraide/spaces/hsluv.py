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
from ..spaces import Space, RE_DEFAULT_MATCH, FLG_ANGLE, FLG_PERCENT, GamutBound, Cylindrical
from .lch import ACHROMATIC_THRESHOLD
from .lab import EPSILON, KAPPA
from .srgb_linear import XYZ_TO_RGB
import re
import math
from .. import util
from ..util import MutableVector
from typing import List, Dict, Tuple


def length_of_ray_until_intersect(theta: float, line: Dict[str, float]) -> float:
    """Length of ray until intersect."""

    return line['intercept'] / (math.sin(theta) - line['slope'] * math.cos(theta))


def get_bounds(l: float) -> List[Dict[str, float]]:
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


def hsluv_to_lch(hsluv: MutableVector) -> MutableVector:
    """Convert HSLuv to Lch."""

    h, s, l = hsluv
    h = util.no_nan(h)
    c = 0.0
    if l > 100 - 1e-7:
        l = 100.0
    elif l < 1e-08:
        l = 0.0
    else:
        _hx_max = max_chroma_for_lh(l, h)
        c = _hx_max / 100.0 * s
        if c < ACHROMATIC_THRESHOLD:
            h = util.NaN
    return [l, c, util.constrain_hue(h)]


def lch_to_hsluv(lch: MutableVector) -> MutableVector:
    """Convert Lch to HSLuv."""

    l, c, h = lch
    h = util.no_nan(h)
    s = 0.0
    if l > 100 - 1e-7:
        l = 100.0
    elif l < 1e-08:
        l = 0.0
    else:
        _hx_max = max_chroma_for_lh(l, h)
        s = c / _hx_max * 100.0
    if s < 1e-08:
        h = util.NaN
    return [util.constrain_hue(h), s, l]


class HSLuv(Cylindrical, Space):
    """HSLuv class."""

    BASE = 'lchuv'
    NAME = "hsluv"
    SERIALIZE = ("--hsluv",)
    CHANNEL_NAMES = ("h", "s", "l")
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "lightness": "l"
    }
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"
    GAMUT_CHECK = "srgb"

    BOUNDS = (
        GamutBound(0.0, 360.0, FLG_ANGLE),
        GamutBound(0.0, 100.0, FLG_PERCENT),
        GamutBound(0.0, 100.0, FLG_PERCENT)
    )

    @property
    def h(self) -> float:
        """Hue channel."""

        return self._coords[0]

    @h.setter
    def h(self, value: float) -> None:
        """Shift the hue."""

        self._coords[0] = self._handle_input(value)

    @property
    def s(self) -> float:
        """Saturation channel."""

        return self._coords[1]

    @s.setter
    def s(self, value: float) -> None:
        """Saturate or unsaturate the color by the given factor."""

        self._coords[1] = self._handle_input(value)

    @property
    def l(self) -> float:
        """Lightness channel."""

        return self._coords[2]

    @l.setter
    def l(self, value: float) -> None:
        """Set lightness channel."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def null_adjust(cls, coords: MutableVector, alpha: float) -> Tuple[MutableVector, float]:
        """On color update."""

        if coords[1] == 0 or coords[2] > (100 - 1e-7) or coords[2] < 1e-08:
            coords[0] = util.NaN
        return coords, alpha

    @classmethod
    def to_base(cls, coords: MutableVector) -> MutableVector:
        """To LCHuv from HSLuv."""

        return hsluv_to_lch(coords)

    @classmethod
    def from_base(cls, coords: MutableVector) -> MutableVector:
        """From LCHuv to HSLuv."""

        return lch_to_hsluv(coords)
