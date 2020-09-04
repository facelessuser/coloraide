"""HSL class."""
from .base import _Color
from .tools import _ColorTools
from .. import parse
from .. import util
from ..util import convert


class _HSL(_ColorTools, _Color):
    """HSL class."""

    COLORSPACE = "hsl"
    DEF_BG = "[0, 0, 0, 1]"

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, _Color):
            if color.get_colorspace() == "hsl":
                self._ch, self._cs, self._cl, self._alpha = color._ch, color._cs, color._cl, color._alpha
            elif color.get_colorspace() == "srgb":
                self._ch, self._cs, self._cl = convert.rgb_to_hsl(color._cr, color._cg, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "hwb":
                self._ch, self._cs, self._cl = convert.hwb_to_hsl(color._ch, color._cw, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "lab":
                self._ch, self._cs, self._cl = convert.lab_to_hsl(color._cl, color._ca, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "lch":
                self._ch, self._cs, self._cl = convert.lch_to_hsl(color._cl, color._cc, color._ch)
                self._alpha = color._alpha
            else:
                raise TypeError("Unexpected color space '{}' received".format(color.get_colorspace()))
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._ch, self._cs, self._cl, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._ch = color[0]
            self._cs = color[1]
            self._cl = color[2]
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
    def _cs(self):
        """Saturation channel."""

        return self._c2

    @_cs.setter
    def _cs(self, value):
        """Set saturation channel."""

        self._c2 = util.clamp(value, 0.0, 1.0)

    @property
    def _cl(self):
        """Lightness channel."""

        return self._c3

    @_cl.setter
    def _cl(self, value):
        """Set lightness channel."""

        self._c3 = util.clamp(value, 0.0, 1.0)

    def __str__(self):
        """String."""

        return self.to_string(alpha=True)

    def is_achromatic(self, scale=util.INF):
        """Check if the color is achromatic."""

        return util.round_half_up(self._cs * 360.0, scale) <= 0.0

    def _grayscale(self):
        """Convert to grayscale."""

        self._c1 = 0.0
        self._cs = 0.0

    def _mix(self, color, factor, factor2=1.0):
        """Blend the color with the given color."""

        self._ch = self._hue_mix_channel(self._ch, color._ch, factor, factor2)
        self._cl = self._mix_channel(self._cl, color._cl, factor, factor2)
        self._cs = self._mix_channel(self._cs, color._cs, factor, factor2)

    @property
    def hue(self):
        """Hue channel."""

        return self._ch

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._ch = self.tx_channel(0, value) if isinstance(value, str) else float(value)

    @property
    def saturation(self):
        """Saturation channel."""

        return self._cs

    @saturation.setter
    def saturation(self, value):
        """Saturate or unsaturate the color by the given factor."""

        self._cs = self.tx_channel(1, value) if isinstance(value, str) else float(value)

    @property
    def lightness(self):
        """Lightness channel."""

        return self._cl

    @lightness.setter
    def lightness(self, value):
        """Set lightness channel."""

        self._cl = self.tx_channel(2, value) if isinstance(value, str) else float(value)

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
