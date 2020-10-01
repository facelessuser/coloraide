"""HSV class."""
from ._space import Space, RE_DEFAULT_MATCH
from ._gamut import GamutBound, GamutAngle
from . import _convert as convert
from . import _parse as parse
from .. import util
import re


class HSV(Space):
    """HSL class."""

    SPACE = "hsv"
    DEF_BG = "color(hsv 0 0 0 / 1)"
    CHANNEL_NAMES = frozenset(["hue", "saturation", "value", "alpha"])
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
            self.hue, self.saturation, self.value = convert.convert(color.coords(), color.space(), self.space())
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

    def _is_achromatic(self, coords):
        """Is achromatic."""

        h, s, v = [util.round_half_up(c, scale=util.DEF_PREC) for c in coords]
        return s < util.ACHROMATIC_THRESHOLD

    def _on_convert(self):
        """
        Run after a convert operation.

        Gives us an opportunity to normalize hues and things like that, if we desire.
        """

        if not (0.0 <= self.hue <= 360.0):
            self.hue = self.hue % 360.0

    def _mix(self, channels1, channels2, factor, factor2=1.0, hue=util.DEF_HUE_ADJ, **kwargs):
        """Blend the color with the given color."""

        hue1 = util.NAN if self._is_achromatic(channels1) else channels1[0]
        hue2 = util.NAN if self._is_achromatic(channels2) else channels2[0]
        return (
            self._hue_mix_channel(hue1, hue2, factor, factor2, hue=hue),
            self._mix_channel(channels1[1], channels2[1], factor, factor2),
            self._mix_channel(channels1[2], channels2[2], factor, factor2)
        )

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
    def value(self):
        """Value channel."""

        return self._coords[2]

    @value.setter
    def value(self, value):
        """Set value channel."""

        self._coords[2] = self.translate_channel(2, value) if isinstance(value, str) else float(value)

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel == 0:
            return parse.norm_deg_channel(value)
        elif channel in (1, 2):
            return float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:
            raise ValueError("Unexpected channel index of '{}'".format(channel))

    def to_string(self, *, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs):
        """To string."""

        return super().to_string(alpha=alpha, precision=precision, fit=fit)
