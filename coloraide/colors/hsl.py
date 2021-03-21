"""HSL class."""
from ._space import Space, RE_DEFAULT_MATCH
from .srgb import SRGB
from ._cylindrical import Cylindrical
from ._gamut import GamutBound
from . _range import Angle, Percent
from . import _parse as parse
from . import _convert as convert
from .. import util
import re


def srgb_to_hsl(rgb):
    """SRGB to HSL."""

    r, g, b = rgb
    mx = max(rgb)
    mn = min(rgb)
    h = util.NaN
    s = 0.0
    l = (mn + mx) / 2
    c = mx - mn

    if c != 0.0:
        if mx == r:
            h = (g - b) / c
        elif mx == g:
            h = (b - r) / c + 2.0
        else:
            h = (r - g) / c + 4.0
        s = 0 if l == 0 or l == 1 else (mx - l) / min(l, 1 - l)
        h *= 60.0

    return HSL._constrain_hue(h), s * 100.0, l * 100.0


def hsl_to_srgb(hsl):
    """
    HSL to RGB.

    https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB_alternative
    """

    h, s, l = hsl
    h = util.no_nan(h)
    h = h % 360
    s /= 100.0
    l /= 100.0

    def f(n):
        """Calculate the channels."""
        k = (n + h / 30) % 12
        a = s * min(l, 1 - l)
        return l - a * max(-1, min(k - 3, 9 - k, 1))

    return f(0), f(8), f(4)


class HSL(Cylindrical, Space):
    """HSL class."""

    SPACE = "hsl"
    DEF_VALUE = "color(hsl 0 0 0 / 1)"
    CHANNEL_NAMES = frozenset(["hue", "saturation", "lightness", "alpha"])
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
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
            self.hue, self.saturation, self.lightness = color.convert(self.space()).coords()
            self.alpha = color.alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self.hue, self.saturation, self.lightness, self.alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self.hue = color[0]
            self.saturation = color[1]
            self.lightness = color[2]
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
    def lightness(self):
        """Lightness channel."""

        return self._coords[2]

    @lightness.setter
    def lightness(self, value):
        """Set lightness channel."""

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
    def _to_srgb(cls, hsl):
        """To sRGB."""

        return hsl_to_srgb(hsl)

    @classmethod
    def _from_srgb(cls, rgb):
        """From sRGB."""

        return srgb_to_hsl(rgb)

    @classmethod
    def _to_xyz(cls, hsl):
        """To XYZ."""

        return SRGB._to_xyz(cls._to_srgb(hsl))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return cls._from_srgb(SRGB._from_xyz(xyz))
