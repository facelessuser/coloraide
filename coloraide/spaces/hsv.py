"""HSV class."""
from ..spaces import Space, RE_DEFAULT_MATCH, Angle, Percent, GamutBound, Cylindrical
from .srgb.base import SRGB
from .hsl.base import HSL
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
        util.constrain_hue(h),
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

    return [util.constrain_hue(h), s * 100.0, v * 100.0]


class HSV(Cylindrical, Space):
    """HSL class."""

    SPACE = "hsv"
    SERIALIZE = ("--hsv",)
    CHANNEL_NAMES = ("hue", "saturation", "value", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    GAMUT_CHECK = "srgb"
    WHITE = "D65"

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
    def _to_xyz(cls, parent, hsv):
        """To XYZ."""

        return SRGB._to_xyz(parent, cls._to_srgb(parent, hsv))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return cls._from_srgb(parent, SRGB._from_xyz(parent, xyz))

    @classmethod
    def _to_hsl(cls, parent, hsv):
        """To HSL."""

        return hsv_to_hsl(hsv)

    @classmethod
    def _from_hsl(cls, parent, hsl):
        """From HSL."""

        return hsl_to_hsv(hsl)

    @classmethod
    def _to_srgb(cls, parent, hsv):
        """To sRGB."""

        return HSL._to_srgb(parent, cls._to_hsl(parent, hsv))

    @classmethod
    def _from_srgb(cls, parent, rgb):
        """From sRGB."""

        return cls._from_hsl(parent, HSL._from_srgb(parent, rgb))
