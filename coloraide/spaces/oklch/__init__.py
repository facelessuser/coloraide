"""
LCH class.

---- License ----

Copyright (c) 2021 Björn Ottosson

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

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
from ...spaces import Space, Lchish
from ...cat import WHITES
from ...gamut.bounds import GamutUnbound, FLG_ANGLE, FLG_OPT_PERCENT
from ... import util
import math
from ... import algebra as alg
from ...types import Vector
from typing import Tuple

ACHROMATIC_THRESHOLD = 0.000002


def oklab_to_oklch(oklab: Vector) -> Vector:
    """Oklab to Oklch."""

    l, a, b = oklab

    c = math.sqrt(a ** 2 + b ** 2)
    h = math.degrees(math.atan2(b, a))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = alg.NaN

    return [l, c, util.constrain_hue(h)]


def oklch_to_oklab(oklch: Vector) -> Vector:
    """Oklch to Oklab."""

    l, c, h = oklch
    if alg.is_nan(h):  # pragma: no cover
        return [l, 0.0, 0.0]

    return [
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    ]


class Oklch(Lchish, Space):
    """Oklch class."""

    BASE = "oklab"
    NAME = "oklch"
    SERIALIZE = ("--oklch",)
    CHANNEL_NAMES = ("l", "c", "h")
    CHANNEL_ALIASES = {
        "lightness": "l",
        "chroma": "c",
        "hue": "h"
    }
    WHITE = WHITES['2deg']['D65']

    BOUNDS = (
        GamutUnbound(0.0, 1.0, FLG_OPT_PERCENT),
        GamutUnbound(0.0, 1.0),
        GamutUnbound(0.0, 360.0, FLG_ANGLE)
    )

    @property
    def l(self) -> float:
        """Lightness."""

        return self._coords[0]

    @l.setter
    def l(self, value: float) -> None:
        """Get true luminance."""

        self._coords[0] = value

    @property
    def c(self) -> float:
        """Chroma."""

        return self._coords[1]

    @c.setter
    def c(self, value: float) -> None:
        """chroma."""

        self._coords[1] = alg.clamp(value, 0.0)

    @property
    def h(self) -> float:
        """Hue."""

        return self._coords[2]

    @h.setter
    def h(self, value: float) -> None:
        """Shift the hue."""

        self._coords[2] = value

    @classmethod
    def null_adjust(cls, coords: Vector, alpha: float) -> Tuple[Vector, float]:
        """On color update."""

        coords = alg.no_nans(coords)
        if coords[1] < ACHROMATIC_THRESHOLD:
            coords[2] = alg.NaN

        return coords, alg.no_nan(alpha)

    @classmethod
    def to_base(cls, oklch: Vector) -> Vector:
        """To Lab."""

        return oklch_to_oklab(oklch)

    @classmethod
    def from_base(cls, oklab: Vector) -> Vector:
        """To Lab."""

        return oklab_to_oklch(oklab)
