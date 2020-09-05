"""HWB class."""
from .base import _Color
from .tools import _ColorTools
from .. import parse
from ..util import convert
from .. import util


class _HWB(_ColorTools, _Color):
    """HWB class."""

    COLORSPACE = "hwb"
    DEF_BG = "[0, 0, 0, 1]"

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, _Color):
            if color.space() == "hwb":
                self._ch, self._cw, self._cb, self._alpha = color._ch, color._cw, color._cb, color._alpha
            elif color.space() == "srgb":
                self._ch, self._cw, self._cb = convert.rgb_to_hwb(color._cr, color._cg, color._cb)
                self._alpha = color._alpha
            elif color.space() == "hsl":
                self._ch, self._cw, self._cb = convert.hsl_to_hwb(color._ch, color._cs, color._cl)
                self._alpha = color._alpha
            elif color.space() == "lab":
                self._ch, self._cw, self._cb = convert.lab_to_hwb(color._cl, color._ca, color._cb)
                self._alpha = color._alpha
            elif color.space() == "lch":
                self._ch, self._cw, self._cb = convert.lch_to_hwb(color._cl, color._cc, color._ch)
                self._alpha = color._alpha
            else:
                raise TypeError("Unexpected color space '{}' received".format(color.space()))
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._ch, self._cw, self._cb, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._ch = color[0]
            self._cw = color[1]
            self._cb = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    @property
    def _ch(self):
        """Hue channel."""

        return self._c1

    @_ch.setter
    def _ch(self, value):
        """Set hue channel."""

        self._c1 = value if 0.0 <= value <= 1.0 else value % 1.0

    @property
    def _cw(self):
        """Whiteness channel."""

        return self._c2

    @_cw.setter
    def _cw(self, value):
        """Set whiteness channel."""

        self._c2 = util.clamp(value, 0.0, 1.0)

    @property
    def _cb(self):
        """Blackness channel."""

        return self._c3

    @_cb.setter
    def _cb(self, value):
        """Set blackness channel."""

        self._c3 = util.clamp(value, 0.0, 1.0)

    def is_achromatic(self, scale=util.INF):
        """Check if the color is achromatic."""

        return util.round_half_up(self._cw * 100.0, scale) + util.round_half_up(self._cb * 100.0, scale) >= 100.0

    def _grayscale(self):
        """Convert to grayscale."""

        factor = 1.0 / (self._cw + self._cb)
        self._c2 = self._cw + factor
        self._c3 = self._cb + factor

    def _mix(self, color, factor, factor2=1.0):
        """Blend the color with the given color."""

        self._ch = self._hue_mix_channel(self._ch, color._ch, factor, factor2)
        self._cw = self._mix_channel(self._cw, color._cw, factor, factor2)
        self._cb = self._mix_channel(self._cb, color._cb, factor, factor2)

    @property
    def hue(self):
        """Hue channel."""

        return self._ch

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._ch = self.tx_channel(1, value) if isinstance(value, str) else float(value)

    @property
    def whiteness(self):
        """Whiteness channel."""

        return self._cw

    @whiteness.setter
    def whiteness(self, value):
        """Set whiteness channel."""

        self._cw = self.tx_channel(2, value) if isinstance(value, str) else float(value)

    @property
    def blackness(self):
        """Blackness channel."""

        return self._cb

    @blackness.setter
    def blackness(self, value):
        """Set blackness channel."""

        self._cb = self.tx_channel(3, value) if isinstance(value, str) else float(value)

    @classmethod
    def tx_channel(cls, channel, value):
        """Translate channel string."""

        if channel == 0:
            return parse.norm_deg_channel(value, 1.0)
        elif channel in (1, 2):
            return float(value)
        elif channel == -1:
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
