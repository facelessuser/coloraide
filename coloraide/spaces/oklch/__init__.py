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
from ..oklab import xyz_d65_to_oklab
from ..lch import LCh, lab_to_lch
from ...spaces import Space
from ...cat import WHITES
from ...channels import Channel, FLG_ANGLE, FLG_OPT_PERCENT
from ... import util


class OkLCh(LCh, Space):
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
    # OkLCh serializes undefined hues to 0 in CSS, so we will use this to improve conversions,
    # but still serialize undefined hues to 0 as it puts us still in range, but we get better
    # round tripping with the hue below.
    ACHROMATIC_HUE = lab_to_lch(xyz_d65_to_oklab(util.xy_to_xyz(WHITE)))[-1]

    def achromatic_hue(self) -> float:
        """
        Ideal achromatic hue.

        This is the ideal achromatic hue. It tightens up translation, but we can get away
        with accepting 0 as well.
        """

        return self.ACHROMATIC_HUE
