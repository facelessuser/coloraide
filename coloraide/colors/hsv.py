"""HSV class."""
from ._space import Space, RE_DEFAULT_MATCH
from .srgb import SRGB
from .hsl import HSL
from ._cylindrical import Cylindrical
from ._gamut import GamutBound
from . _range import Angle, Percent
from . import _convert as convert
from .. import util
import re


def hsv_to_hsl(hsv):
    """
    HSV to HSL.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    h, s, v = hsv
    s /= 100.0
    v /= 100.0
    l = v * (1.0 - s / 2.0)
    s = 0.0 if (l == 0.0 or l == 1.0) else ((v - l) / min(l, 1.0 - l)) * 100

    if s == 0:
        h = util.NaN

    return [
        HSV._constrain_hue(h),
        s,
        l * 100
    ]


def hsl_to_hsv(hsl):
    """
    HSL to HSV.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    h, s, l = hsl
    s /= 100.0
    l /= 100.0

    v = l + s * min(l, 1.0 - l)
    s = 0.0 if (v == 0.0) else 2 * (1.0 - l / v)

    if s == 0:
        h = util.NaN

    return [HSV._constrain_hue(h), s * 100.0, v * 100.0]


class HSV(Cylindrical, Space):
    """HSL class."""

    SPACE = "hsv"
    CHANNEL_NAMES = ("hue", "saturation", "value", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    GAMUT_CHECK = "hsl"
    WHITE = convert.WHITES["D65"]

    _range = (
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
    def _to_xyz(cls, hsv):
        """To XYZ."""

        return SRGB._to_xyz(cls._to_srgb(hsv))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return cls._from_srgb(SRGB._from_xyz(xyz))

    @classmethod
    def _to_hsl(cls, hsv):
        """To HSL."""

        return hsv_to_hsl(hsv)

    @classmethod
    def _from_hsl(cls, hsl):
        """From HSL."""

        return hsl_to_hsv(hsl)

    @classmethod
    def _to_srgb(cls, hsv):
        """To sRGB."""

        return HSL._to_srgb(cls._to_hsl(hsv))

    @classmethod
    def _from_srgb(cls, rgb):
        """From sRGB."""

        return cls._from_hsl(HSL._from_srgb(rgb))
