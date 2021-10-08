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
from .xyz import XYZ
from .. import util
import re

# sRGB Linear to LMS
SRGBL_TO_LMS = [
    [0.4122214708, 0.5363325363, 0.0514459929],
    [0.2119034982, 0.6806995451, 0.1073969566],
    [0.0883024619, 0.2817188376, 0.6299787005]
]

# LMS to sRGB Linear
LMS_TO_SRGBL = [
    [4.076741661347995, -3.3077115904081937, 0.23096992872942781],
    [-1.268438004092176, 2.6097574006633715, -0.3413193963102195],
    [-0.004196086541836995, -0.7034186144594496, 1.7076147009309446]
]

# LMS ** 1/3 to Oklab
LMS3_TO_OKLAB = [
    [0.2104542553, 0.793617785, -0.0040720468],
    [1.9779984951, -2.428592205, 0.4505937099],
    [0.0259040371, 0.7827717662, -0.808675766]
]

# Oklab to LMS ** 1/3
OKLAB_TO_LMS3 = [
    [0.9999999984505199, 0.3963377921737679, 0.2158037580607588],
    [1.0000000088817607, -0.10556134232365635, -0.06385417477170591],
    [1.0000000546724108, -0.08948418209496575, -1.2914855378640917]
]

# XYZ D65 to LMS
XYZD65_TO_LMS = [
    [0.8190224432164319, 0.3619062562801221, -0.12887378261216417],
    [0.0329836671980271, 0.9292868468965546, 0.0361446681699984],
    [0.04817719956604624, 0.2642395249442277, 0.6335478258136936]
]

# LMS to XYZ
LMS_TO_XYZD65 = [
    [1.2268798733741557, -0.5578149965554813, 0.28139105017721594],
    [-0.04057576262431372, 1.1122868293970594, -0.07171106666151696],
    [-0.07637294974672142, -0.4214933239627916, 1.5869240244272422]
]


def oklab_to_linear_srgb(lab):
    """Convert from Oklab to linear sRGB."""

    return util.dot(LMS_TO_SRGBL, [c ** 3 for c in util.dot(OKLAB_TO_LMS3, lab)])


def linear_srgb_to_oklab(rgb):
    """Linear sRGB to Oklab."""

    return util.dot(LMS3_TO_OKLAB, [util.cbrt(c) for c in util.dot(SRGBL_TO_LMS, rgb)])


def oklab_to_xyz_d65(lab):
    """Convert from Oklab to linear sRGB."""

    return util.dot(LMS_TO_XYZD65, [c ** 3 for c in util.dot(OKLAB_TO_LMS3, lab)])


def xyz_d65_to_oklab(rgb):
    """Linear sRGB to Oklab."""

    return util.dot(LMS3_TO_OKLAB, [util.cbrt(c) for c in util.dot(XYZD65_TO_LMS, rgb)])


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
    def _to_srgb(cls, parent, oklab):
        """To sRGB."""

        return SRGBLinear._to_srgb(parent, cls._to_srgb_linear(parent, oklab))

    @classmethod
    def _from_srgb(cls, parent, srgb):
        """From sRGB."""

        return cls._from_srgb_linear(parent, SRGBLinear._from_srgb(parent, srgb))

    @classmethod
    def _to_srgb_linear(cls, parent, oklab):
        """To sRGB Linear."""

        return oklab_to_linear_srgb(oklab)

    @classmethod
    def _from_srgb_linear(cls, parent, srgbl):
        """From SRGB Linear."""

        return linear_srgb_to_oklab(srgbl)

    @classmethod
    def _to_xyz(cls, parent, oklab):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, oklab_to_xyz_d65(oklab))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return xyz_d65_to_oklab(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz))
