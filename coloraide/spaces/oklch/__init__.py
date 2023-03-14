"""
OkLCh class.

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
from __future__ import annotations
from ...spaces import Space, LChish
from ...cat import WHITES
from ...channels import Channel, FLG_ANGLE, FLG_OPT_PERCENT
from ... import util
import math
from ...types import Vector

# The transform consistently yields ~90˚ for achromatic hues for positive lightness
# Replacing achromatic NaN hues with this hue gives us closer translations back.
# Negative lightness uses ~270, but not worth handling as real world colors don't
# use inverse lightness.
ACHROMATIC_HUE = 90.00000025580869


def oklab_to_oklch(oklab: Vector) -> Vector:
    """Oklab to OkLCh."""

    l, a, b = oklab

    c = math.sqrt(a ** 2 + b ** 2)
    h = math.degrees(math.atan2(b, a))

    return [l, c, util.constrain_hue(h)]


def oklch_to_oklab(oklch: Vector) -> Vector:
    """OkLCh to Oklab."""

    l, c, h = oklch

    return [
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    ]


class OkLCh(LChish, Space):
    """OkLCh class."""

    BASE = "oklab"
    NAME = "oklch"
    SERIALIZE = ("--oklch",)
    CHANNELS = (
        Channel("l", 0.0, 1.0, flags=FLG_OPT_PERCENT),
        Channel("c", 0.0, 0.4, limit=(0.0, None), flags=FLG_OPT_PERCENT),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )
    CHANNEL_ALIASES = {
        "lightness": "l",
        "chroma": "c",
        "hue": "h"
    }
    WHITE = WHITES['2deg']['D65']

    def achromatic_hue(self) -> float:
        """
        Ideal achromatic hue.

        This is the ideal achromatic hue. It tightens up translation, but we can get away
        with accepting 0 as well.
        """

        return ACHROMATIC_HUE

    def to_base(self, oklch: Vector) -> Vector:
        """To Lab."""

        return oklch_to_oklab(oklch)

    def from_base(self, oklab: Vector) -> Vector:
        """To Lab."""

        return oklab_to_oklch(oklab)
