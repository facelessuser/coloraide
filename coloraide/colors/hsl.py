"""HSL class."""
import re
from ._base import _Color
from ._tools import _ColorTools, GamutBound, GamutHue
from .. import util
from ..util import parse
from ..util import convert


class _HSL(_ColorTools, _Color):
    """HSL class."""

    SPACE = "hsl"
    DEF_BG = "color(hsl 0 0 0 / 1)"
    _MATCH = re.compile(
        r"(?xi)color\(\s*hsl\s+((?:{float}{sep}){{2}}{float}(?:{asep}(?:{percent}|{float}))?)\s*\)".format(
            **parse.COLOR_PARTS
        )
    )

    _gamut = (
        (GamutHue(0.0), GamutHue(360.0)),
        (GamutBound(0.0), GamutBound(100.0)),
        (GamutBound(0.0), GamutBound(100.0))
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, _Color):
            self._ch, self._cs, self._cl = convert.convert(color._channels, color.space(), self.space())
            self._alpha = color._alpha
        elif isinstance(color, str):
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

        return self._channels[0]

    @_ch.setter
    def _ch(self, value):
        """Set hue channel."""

        self._channels[0] = value

    @property
    def _cs(self):
        """Saturation channel."""

        return self._channels[1]

    @_cs.setter
    def _cs(self, value):
        """Set saturation channel."""

        self._channels[1] = value

    @property
    def _cl(self):
        """Lightness channel."""

        return self._channels[2]

    @_cl.setter
    def _cl(self, value):
        """Set lightness channel."""

        self._channels[2] = value

    def __str__(self):
        """String."""

        return self.to_string(alpha=True)

    def _grayscale(self):
        """Convert to grayscale."""

        self._ch = 0.0
        self._cs = 0.0

    def _mix(self, channels1, channels2, factor, factor2=1.0):
        """Blend the color with the given color."""

        if self._is_achromatic(channels1):
            channels1[0] = util.NAN
        if self._is_achromatic(channels2):
            channels2[0] = util.NAN
        self._ch = self._hue_mix_channel(channels1[0], channels2[0], factor, factor2)
        self._cl = self._mix_channel(channels1[1], channels2[1], factor, factor2)
        self._cs = self._mix_channel(channels1[2], channels2[2], factor, factor2)

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
            return parse.norm_deg_channel(value)
        elif channel in (1, 2):
            return float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)

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
