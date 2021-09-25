"""
Okhsv class.

Translation to/from Oklab is licensed under MIT by the original author, all
other code also licensed under MIT: Copyright (c) 2021 Isaac Muse.

---- Oklab license ----

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
from ..spaces import Space, RE_DEFAULT_MATCH, Angle, Percent, GamutBound, Cylindrical
from ..spaces.srgb.base import lin_srgb, gam_srgb
from ..spaces.oklab import Oklab
from .. import util
from .okhsl import linear_srgb_to_oklab, oklab_to_linear_srgb, toe, toe_inv, find_cusp, to_st
import re
import math


def okhsv_to_oklab(hsv):
    """Convert from Okhsv to Oklab."""

    h, s, v = hsv
    s /= 100
    v /= 100
    h = util.no_nan(h) / 360.0

    l = toe_inv(v)
    a = b = 0

    if l != 0 and s != 0:
        a_ = math.cos(2.0 * math.pi * h)
        b_ = math.sin(2.0 * math.pi * h)

        cusp = find_cusp(a_, b_)
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
        rs, gs, bs = oklab_to_linear_srgb([l_vt, a_ * c_vt, b_ * c_vt])
        scale_l = util.nth_root(1.0 / max(max(rs, gs), max(bs, 0.0)), 3)

        l = l * scale_l
        c = c * scale_l

        a = c * a_
        b = c * b_

    return [l, a, b]


def oklab_to_okhsv(lab):
    """Oklab to Okhsv."""

    c = math.sqrt(lab[1] ** 2 + lab[2] ** 2)
    l = lab[0]

    h = util.NaN
    s = 0
    v = toe(l)

    if c != 0 and l != 0 and l != 1:
        a_ = lab[1] / c
        b_ = lab[2] / c

        h = 0.5 + 0.5 * math.atan2(-lab[2], -lab[1]) / math.pi

        cusp = find_cusp(a_, b_)
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
        rs, gs, bs = oklab_to_linear_srgb([l_vt, a_ * c_vt, b_ * c_vt])
        scale_l = util.nth_root(1.0 / max(max(rs, gs), max(bs, 0.0)), 3)

        l = l / scale_l
        c = c / scale_l

        c = c * toe(l) / l
        l = toe(l)

        # we can now compute v and s:
        v = l / l_v
        s = (s_0 + t_max) * c_v / ((t_max * s_0) + t_max * k * c_v)

    if s == 0:
        h = util.NaN

    return [util.constrain_hue(h * 360), s * 100, v * 100]


def srgb_to_okhsv(srgb):
    """SRGB to Okhsv."""

    return oklab_to_okhsv(linear_srgb_to_oklab(lin_srgb(srgb)))


def okhsv_to_srgb(hsv):
    """Okhsv to sRGB."""

    return gam_srgb(oklab_to_linear_srgb(okhsv_to_oklab(hsv)))


class Okhsv(Cylindrical, Space):
    """Okhsv class."""

    SPACE = "okhsv"
    SERIALIZE = ("--okhsv",)
    CHANNEL_NAMES = ("hue", "saturation", "value", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"
    GAMUT_CHECK = "srgb"

    RANGE = (
        GamutBound([Angle(0.0), Angle(360.0)]),
        GamutBound([Percent(0.0), Percent(100.0)]),
        GamutBound([Percent(0.0), Percent(100.0)])
    )

    @property
    def hue(self):
        """Hue channel."""

        return self._coords[0]

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._coords[0] = self._handle_input(value)

    @property
    def saturation(self):
        """Saturation channel."""

        return self._coords[1]

    @saturation.setter
    def saturation(self, value):
        """Saturate or unsaturate the color by the given factor."""

        self._coords[1] = self._handle_input(value)

    @property
    def value(self):
        """Value channel."""

        return self._coords[2]

    @value.setter
    def value(self, value):
        """Set value channel."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def null_adjust(cls, coords, alpha):
        """On color update."""

        if coords[1] == 0:
            coords[0] = util.NaN
        return coords, alpha

    @classmethod
    def _to_srgb(cls, parent, hsl):
        """To sRGB."""

        return okhsv_to_srgb(hsl)

    @classmethod
    def _from_srgb(cls, parent, srgb):
        """From sRGB."""

        return srgb_to_okhsv(srgb)

    @classmethod
    def _to_xyz(cls, parent, hsl):
        """To XYZ."""

        return Oklab._to_xyz(parent, okhsv_to_oklab(hsl))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return oklab_to_okhsv(Oklab._from_xyz(parent, xyz))
