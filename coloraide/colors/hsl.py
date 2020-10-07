"""HSL class."""
from ._space import Space, RE_DEFAULT_MATCH
from ._gamut import GamutBound, GamutAngle
from . import _parse as parse
from . import _convert as convert
from .. import util
import re


class HSL(Space):
    """HSL class."""

    SPACE = "hsl"
    DEF_BG = "color(hsl 0 0 0 / 1)"
    CHANNEL_NAMES = frozenset(["hue", "saturation", "lightness", "alpha"])
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))

    _gamut = (
        (GamutAngle(0.0), GamutAngle(360.0)),
        (GamutBound(0.0), GamutBound(100.0)),
        (GamutBound(0.0), GamutBound(100.0))
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, Space):
            self.hue, self.saturation, self.lightness = convert.convert(color.coords(), color.space(), self.space())
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

    def _is_achromatic(self, coords):
        """Is achromatic."""

        h, s, l = [util.round_half_up(c, scale=util.DEF_PREC) for c in coords]
        return (
            s < util.ACHROMATIC_THRESHOLD or
            ((0 + util.ACHROMATIC_THRESHOLD) > l or l > (100.0 - util.ACHROMATIC_THRESHOLD))
        )

    def _on_convert(self):
        """
        Run after a convert operation.

        Gives us an opportunity to normalize hues and things like that, if we desire.
        """

        if not (0.0 <= self.hue <= 360.0):
            self.hue = self.hue % 360.0

    @property
    def hue(self):
        """Hue channel."""

        return self._coords[0]

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._coords[0] = self.translate_channel(0, value) if isinstance(value, str) else float(value)

    @property
    def saturation(self):
        """Saturation channel."""

        return self._coords[1]

    @saturation.setter
    def saturation(self, value):
        """Saturate or unsaturate the color by the given factor."""

        self._coords[1] = self.translate_channel(1, value) if isinstance(value, str) else float(value)

    @property
    def lightness(self):
        """Lightness channel."""

        return self._coords[2]

    @lightness.setter
    def lightness(self, value):
        """Set lightness channel."""

        self._coords[2] = self.translate_channel(2, value) if isinstance(value, str) else float(value)

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
    def split_channels(cls, color):
        """Split channels."""

        channels = []
        for i, c in enumerate(parse.RE_COMMA_SPLIT.split(color[1:-1].strip()), 0):
            if i <= 2:
                channels.append(cls.translate_channel(i, c))
            else:
                channels.append(cls.translate_channel(-1, c))
        if len(channels) == 3:
            channels.append(1.0)
        return channels

    def to_string(self, *, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs):
        """To string."""

        return super().to_string(alpha=alpha, precision=precision, fit=fit)
