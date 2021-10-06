"""HSL class."""
from ...spaces import OptionalPercent, Space, RE_DEFAULT_MATCH, Angle, GamutBound, Cylindrical
from ..srgb.base import SRGB
from ... import util
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
        if s == 0:
            h = util.NaN

    return [util.constrain_hue(h), s, l]


def hsl_to_srgb(hsl):
    """
    HSL to RGB.

    https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB_alternative
    """

    h, s, l = hsl
    h = util.no_nan(h)
    h = h % 360

    def f(n):
        """Calculate the channels."""
        k = (n + h / 30) % 12
        a = s * min(l, 1 - l)
        return l - a * max(-1, min(k - 3, 9 - k, 1))

    return [f(0), f(8), f(4)]


class HSL(Cylindrical, Space):
    """HSL class."""

    SPACE = "hsl"
    SERIALIZE = ("--hsl",)
    CHANNEL_NAMES = ("h", "s", "l", "alpha")
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "lightness": "l"
    }
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"
    GAMUT_CHECK = "srgb"

    RANGE = (
        GamutBound([Angle(0.0), Angle(360.0)]),
        GamutBound([OptionalPercent(0.0), OptionalPercent(1.0)]),
        GamutBound([OptionalPercent(0.0), OptionalPercent(1.0)])
    )

    @property
    def h(self):
        """Hue channel."""

        return self._coords[0]

    @h.setter
    def h(self, value):
        """Shift the hue."""

        self._coords[0] = self._handle_input(value)

    @property
    def s(self):
        """Saturation channel."""

        return self._coords[1]

    @s.setter
    def s(self, value):
        """Saturate or unsaturate the color by the given factor."""

        self._coords[1] = self._handle_input(value)

    @property
    def l(self):
        """Lightness channel."""

        return self._coords[2]

    @l.setter
    def l(self, value):
        """Set lightness channel."""

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

        return hsl_to_srgb(hsl)

    @classmethod
    def _from_srgb(cls, parent, rgb):
        """From sRGB."""

        return srgb_to_hsl(rgb)

    @classmethod
    def _to_xyz(cls, parent, hsl):
        """To XYZ."""

        return SRGB._to_xyz(parent, cls._to_srgb(parent, hsl))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return cls._from_srgb(parent, SRGB._from_xyz(parent, xyz))
