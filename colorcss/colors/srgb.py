"""SRGB color class."""
from .base import _Color
from .tools import _ColorTools
from .. import parse
from ..util import convert
from .. import util


class _SRGB(_ColorTools, _Color):
    """SRGB class."""

    COLORSPACE = "srgb"
    DEF_BG = "[0, 0, 0, 1]"

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)
        self._c4 = 0.0

        if isinstance(color, _Color):
            if color.space() == "srgb":
                self._cr, self._cg, self._cb, self._alpha = color._cr, color._cg, color._cb, color._alpha
            elif color.space() == "hsl":
                self._cr, self._cg, self._cb = convert.hsl_to_rgb(color._ch, color._cs, color._cl)
                self._alpha = color._alpha
            elif color.space() == "hwb":
                self._cr, self._cg, self._cb = convert.hwb_to_rgb(color._ch, color._cw, color._cb)
                self._alpha = color._alpha
            elif color.space() == "lab":
                self._cr, self._cg, self._cb = convert.lab_to_rgb(color._cl, color._ca, color._cb)
                self._alpha = color._alpha
            elif color.space() == "lch":
                self._cr, self._cg, self._cb = convert.lch_to_rgb(color._cl, color._cc, color._ch)
                self._alpha = color._alpha
            else:
                raise TypeError("Unexpected color space '{}' received".format(color.space()))
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._cr, self._cg, self._cb, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._cr = color[0]
            self._cg = color[1]
            self._cb = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))
        self._update_hue()

    def _update_hue(self):
        """Update hue."""

        if not self.is_achromatic():
            h = convert.rgb_to_hsv(self._cr, self._cg, self._cb)[0]
            self._c4 = h if 0.0 <= h <= 1.0 else h % 1.0

    def mutate(self, obj):
        """Update from color."""

        if self is obj:
            self._update_hue()
            return

        if not isinstance(obj, type(self)):
            obj = type(self)(obj)

        self._c1 = obj._c1
        self._c2 = obj._c2
        self._c3 = obj._c3
        self._alpha = obj._alpha
        self._update_hue()

    @property
    def _cr(self):
        """Red channel."""

        return self._c1

    @_cr.setter
    def _cr(self, value):
        """Set red channel."""

        self._c1 = util.clamp(value, 0.0, 1.0)

    @property
    def _cg(self):
        """Green channel."""

        return self._c2

    @_cg.setter
    def _cg(self, value):
        """Set green channel."""

        self._c2 = util.clamp(value, 0.0, 1.0)

    @property
    def _cb(self):
        """Blue channel."""

        return self._c3

    @_cb.setter
    def _cb(self, value):
        """Set blue channel."""

        self._c3 = util.clamp(value, 0.0, 1.0)

    @property
    def _ch(self):
        """Hue channel."""

        return self._c4

    @_ch.setter
    def _ch(self, value):
        """Set hue channel."""

        self._c4 = value if 0.0 <= value <= 1.0 else value % 1.0

    def __str__(self):
        """String."""

        return self.to_string(alpha=True)

    def is_achromatic(self, scale=util.INF):
        """Check if the color is achromatic."""

        r = util.round_half_up(self._cr * 255.0, scale)
        g = util.round_half_up(self._cg * 255.0, scale)
        b = util.round_half_up(self._cb * 255.0, scale)

        return r == g and g == b

    def _grayscale(self):
        """Convert to grayscale."""

        self._cr = self.luminance()
        self._cg = self.luminance()
        self._cb = self.luminance()

    def _mix(self, color, factor, factor2=1.0):
        """Blend the color with the given color."""

        self._cr = self._mix_channel(self._cr, color._cr, factor, factor2)
        self._cg = self._mix_channel(self._cg, color._cg, factor, factor2)
        self._cb = self._mix_channel(self._cb, color._cb, factor, factor2)
        self._update_hue()

    @property
    def red(self):
        """Adjust red."""

        return self._cr

    @red.setter
    def red(self, value):
        """Adjust red."""

        self._cr = self.tx_channel(0, value) if isinstance(value, str) else float(value)
        self._update_hue()

    @property
    def green(self):
        """Adjust green."""

        return self._cg

    @green.setter
    def green(self, value):
        """Adjust green."""

        self._cg = self.tx_channel(1, value) if isinstance(value, str) else float(value)
        self._update_hue()

    @property
    def blue(self):
        """Adjust blue."""

        return self._cb

    @blue.setter
    def blue(self, value):
        """Adjust blue."""

        self._cb = self.tx_channel(2, value) if isinstance(value, str) else float(value)
        self._update_hue()

    @classmethod
    def tx_channel(cls, channel, value):
        """Translate channel string."""

        return float(value)

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

        channels = []
        for i, c in enumerate(parse.RE_COMMA_SPLIT.split(color[1:-1].strip()), 0):
            if i <= 2:
                channels.append(cls.tx_channel(i, c))
            else:
                channels.append(cls.tx_channel(-1, c))
        if len(channels) == 3:
            channels.append(1.0)
        return channels
