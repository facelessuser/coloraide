"""
Okhsv class.

Adapted to ColorAide Python and ColorAide by Isaac Muse (2021)

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
from .hsv import HSV
from ..channels import FLG_ANGLE, Channel
from .. import util
from .okhsl import toe, toe_inv, find_cusp, to_st, oklab_to_linear_rgb, LMS_TO_SRGBL, SRGBL_COEFF
import math
from .. import algebra as alg
from ..types import Vector, Matrix


def okhsv_to_oklab(
    hsv: Vector,
    lms_to_rgb: Matrix,
    ok_coeff: list[list[Vector]]
) -> Vector:
    """Convert from Okhsv to Oklab."""

    h, s, v = hsv
    h = h / 360.0

    l = toe_inv(v)

    a = b = 0.0

    # Avoid processing gray or colors with undefined hues
    if l != 0.0 and s != 0.0:
        a_ = math.cos(2.0 * math.pi * h)
        b_ = math.sin(2.0 * math.pi * h)

        cusp = find_cusp(a_, b_, lms_to_rgb, ok_coeff)
        s_max, t_max = to_st(cusp)
        s_0 = 0.5
        k = 1 - s_0 / s_max

        # first we compute L and V as if the gamut is a perfect triangle:

        # L, C when v==1:
        l_v = 1 - s * s_0 / (s_0 + t_max - t_max * k * s)
        c_v = s * t_max * s_0 / (s_0 + t_max - t_max * k * s)

        l = v * l_v
        c = v * c_v

        # then we compensate for both toe and the curved top part of the triangle:
        l_vt = toe_inv(l_v)
        c_vt = c_v * l_vt / l_v

        l_new = toe_inv(l)
        c = c * l_new / l
        l = l_new

        # RGB scale
        rs, gs, bs = oklab_to_linear_rgb([l_vt, a_ * c_vt, b_ * c_vt], lms_to_rgb)
        scale_l = alg.nth_root(1.0 / max(max(rs, gs), max(bs, 0.0)), 3)

        l = l * scale_l
        c = c * scale_l

        a = c * a_
        b = c * b_

    return [l, a, b]


def oklab_to_okhsv(
    lab: Vector,
    lms_to_rgb: Matrix,
    ok_coeff: list[list[Vector]]
) -> Vector:
    """Oklab to Okhsv."""

    l = lab[0]
    s = 0.0
    v = toe(l)

    c = math.sqrt(lab[1] ** 2 + lab[2] ** 2)
    h = 0.5 + 0.5 * math.atan2(-lab[2], -lab[1]) / math.pi

    if l != 0.0 and l != 1 and c != 0.0:
        a_ = lab[1] / c
        b_ = lab[2] / c

        cusp = find_cusp(a_, b_, lms_to_rgb, ok_coeff)
        s_max, t_max = to_st(cusp)
        s_0 = 0.5
        k = 1 - s_0 / s_max

        # first we find `L_v`, `C_v`, `L_vt` and `C_vt`
        t = t_max / (c + l * t_max)
        l_v = t * l
        c_v = t * c

        l_vt = toe_inv(l_v)
        c_vt = c_v * l_vt / l_v

        # we can then use these to invert the step that compensates for the toe and the curved top part of the triangle:
        rs, gs, bs = oklab_to_linear_rgb([l_vt, a_ * c_vt, b_ * c_vt], lms_to_rgb)
        scale_l = alg.nth_root(1.0 / max(max(rs, gs), max(bs, 0.0)), 3)

        l = l / scale_l
        c = c / scale_l

        c = c * toe(l) / l
        l = toe(l)

        # we can now compute v and s:
        v = l / l_v
        s = (s_0 + t_max) * c_v / ((t_max * s_0) + t_max * k * c_v)

    return [util.constrain_hue(h * 360), s, v]


class Okhsv(HSV):
    """Okhsv class."""

    BASE = "oklab"
    NAME = "okhsv"
    SERIALIZE = ("--okhsv",)
    CHANNELS = (
        Channel("h", 0.0, 360.0, bound=True, flags=FLG_ANGLE),
        Channel("s", 0.0, 1.0, bound=True),
        Channel("v", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "value": "v"
    }

    def to_base(self, okhsv: Vector) -> Vector:
        """To Oklab from Okhsv."""

        return okhsv_to_oklab(okhsv, LMS_TO_SRGBL, SRGBL_COEFF)

    def from_base(self, oklab: Vector) -> Vector:
        """From Oklab to Okhsv."""

        return oklab_to_okhsv(oklab, LMS_TO_SRGBL, SRGBL_COEFF)
