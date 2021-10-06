"""
Oklab class.

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
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, OptionalPercent, Labish
from .srgb_linear import SRGBLinear
from .. import util
import re

m1 = [
    [0.4122214708, 0.2119034982, 0.0883024619],
    [0.5363325363, 0.6806995451, 0.2817188376],
    [0.0514459929, 0.1073969566, 0.6299787005]
]

m2 = [
    [0.2104542553, 1.9779984951, 0.0259040371],
    [0.793617785, -2.428592205, 0.7827717662],
    [-0.0040720468, 0.4505937099, -0.808675766]
]

m1i = [
    [4.076741661347995, -1.268438004092176, -0.004196086541836995],
    [-3.3077115904081937, 2.6097574006633715, -0.7034186144594496],
    [0.23096992872942781, -0.3413193963102195, 1.7076147009309446]
]

m2i = [
    [0.9999999984505199, 1.0000000088817607, 1.0000000546724108],
    [0.3963377921737679, -0.10556134232365635, -0.08948418209496575],
    [0.2158037580607588, -0.06385417477170591, -1.2914855378640917]
]


def oklab_to_linear_srgb(lab):
    """Convert from Oklab to linear sRGB."""

    return util.dot([c ** 3 for c in util.dot(lab, m2i)], m1i)


def linear_srgb_to_oklab(rgb):
    """Linear sRGB to Oklab."""

    return util.dot([util.cbrt(c) for c in util.dot(rgb, m1)], m2)


class Oklab(Labish, Space):
    """Oklab class."""

    SPACE = "oklab"
    SERIALIZE = ("--oklab",)
    CHANNEL_NAMES = ("l", "a", "b", "alpha")
    CHANNEL_ALIASES = {
        "lightness": "l"
    }
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    RANGE = (
        GamutUnbound([OptionalPercent(0), OptionalPercent(1)]),
        GamutUnbound([-0.5, 0.5]),
        GamutUnbound([-0.5, 0.5])
    )

    @property
    def l(self):
        """L channel."""

        return self._coords[0]

    @l.setter
    def l(self, value):
        """Get true luminance."""

        self._coords[0] = self._handle_input(value)

    @property
    def a(self):
        """A channel."""

        return self._coords[1]

    @a.setter
    def a(self, value):
        """A axis."""

        self._coords[1] = self._handle_input(value)

    @property
    def b(self):
        """B channel."""

        return self._coords[2]

    @b.setter
    def b(self, value):
        """B axis."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def _to_xyz(cls, parent, oklab):
        """To XYZ."""

        return SRGBLinear._to_xyz(parent, oklab_to_linear_srgb(oklab))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return linear_srgb_to_oklab(SRGBLinear._from_xyz(parent, xyz))
