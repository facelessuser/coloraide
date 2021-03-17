"""HSV class."""
from ._space import Space, RE_DEFAULT_MATCH
from .srgb import SRGB
from .hsl import HSL
from ._cylindrical import Cylindrical
from ._gamut import GamutBound
from . _range import Angle, Percent
from . import _parse as parse
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

    return [
        HSV._constrain_hue(h),
        0.0 if (l == 0.0 or l == 1.0) else ((v - l) / min(l, 1.0 - l)) * 100,
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

    return [
        HSV._constrain_hue(h),
        0.0 if (v == 0.0) else 200.0 * (1.0 - l / v),
        100.0 * v
    ]


class HSV(Cylindrical, Space):
    """HSL class."""

    SPACE = "hsv"
    DEF_VALUE = "color(hsv 0 0 0 / 1)"
    CHANNEL_NAMES = frozenset(["hue", "saturation", "value", "alpha"])
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    GAMUT_CHECK = "hsl"
    WHITE = convert.WHITES["D65"]

    _range = (
        GamutBound([Angle(0.0), Angle(360.0)]),
        GamutBound([Percent(0.0), Percent(100.0)]),
        GamutBound([Percent(0.0), Percent(100.0)])
    )

    def __init__(self, color=DEF_VALUE):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, Space):
            self.hue, self.saturation, self.value = color.convert(self.space()).coords()
            self.alpha = color.alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self.hue, self.saturation, self.value, self.alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self.hue = color[0]
            self.saturation = color[1]
            self.value = color[2]
            self.alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

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
    def null_adjust(cls, coords):
        """On color update."""

        if coords[1] == 0:
            coords[0] = util.NaN
        return coords

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel == 0:
            return parse.norm_deg_channel(value)
        elif channel in (1, 2):
            return parse.norm_float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:
            raise ValueError("Unexpected channel index of '{}'".format(channel))

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
