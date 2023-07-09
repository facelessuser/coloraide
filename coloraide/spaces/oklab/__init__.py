"""
Oklab class.

Adapted to Python for ColorAide by Isaac Muse (2021)

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
from ...cat import WHITES
from ...channels import Channel, FLG_OPT_PERCENT, FLG_MIRROR_PERCENT
from ... import algebra as alg
from ...types import Vector
from ..lab import Lab

# LMS ** 1/3 to Oklab
LMS3_TO_OKLAB = [
    [0.21045426830931402, 0.7936177747023052, -0.004072043011619261],
    [1.9779985324311684, -2.4285922420485795, 0.450593709617411],
    [0.025904042465547825, 0.7827717124575296, -0.8086757549230774]
]

# Oklab to LMS ** 1/3
OKLAB_TO_LMS3 = [
    [1.0, 0.3963377773761749, 0.21580375730991364],
    [1.0, -0.10556134581565857, -0.0638541728258133],
    [1.0, -0.08948417752981186, -1.2914855480194092]
]

# XYZ D65 to LMS
XYZD65_TO_LMS = [
    [0.819022437996703, 0.3619062600528904, -0.1288737815209879],
    [0.03298365393238847, 0.9292868615863434, 0.03614466635064236],
    [0.04817718935962421, 0.2642395317527308, 0.6335478284694309]
]

# LMS to XYZ
LMS_TO_XYZD65 = [
    [1.2268798758459243, -0.5578149944602171, 0.2813910456659647],
    [-0.04057574521480085, 1.1122868032803173, -0.07171105806551636],
    [-0.07637293667466008, -0.42149333240224324, 1.5869240198367818]
]


def oklab_to_xyz_d65(lab: Vector) -> Vector:
    """Convert from Oklab to XYZ D65."""

    return alg.dot(
        LMS_TO_XYZD65,
        [c ** 3 for c in alg.dot(OKLAB_TO_LMS3, lab, dims=alg.D2_D1)],
        dims=alg.D2_D1
    )


def xyz_d65_to_oklab(xyz: Vector) -> Vector:
    """XYZ D65 to Oklab."""

    return alg.dot(
        LMS3_TO_OKLAB,
        [alg.nth_root(c, 3) for c in alg.dot(XYZD65_TO_LMS, xyz, dims=alg.D2_D1)],
        dims=alg.D2_D1
    )


class Oklab(Lab):
    """Oklab class."""

    BASE = "xyz-d65"
    NAME = "oklab"
    SERIALIZE = ("--oklab",)
    CHANNELS = (
        Channel("l", 0.0, 1.0, flags=FLG_OPT_PERCENT),
        Channel("a", -0.4, 0.4, flags=FLG_MIRROR_PERCENT | FLG_OPT_PERCENT),
        Channel("b", -0.4, 0.4, flags=FLG_MIRROR_PERCENT | FLG_OPT_PERCENT)
    )
    CHANNEL_ALIASES = {
        "lightness": "l"
    }
    WHITE = WHITES['2deg']['D65']

    def to_base(self, oklab: Vector) -> Vector:
        """To XYZ."""

        return oklab_to_xyz_d65(oklab)

    def from_base(self, xyz: Vector) -> Vector:
        """From XYZ."""

        return xyz_d65_to_oklab(xyz)
