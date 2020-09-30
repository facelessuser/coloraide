"""LCH class."""
from ._space import Space, RE_GENERIC_MATCH
from ._gamut import GamutUnbound, GamutAngle
from . import _convert as convert
from . import _parse as parse
from .. import util
import re


class LCH(Space):
    """LCH class."""

    SPACE = "lch"
    DEF_BG = "color(lch 0 0 0 / 1)"
    CHANNEL_NAMES = frozenset(["lightness", "chroma", "hue", "alpha"])
    GENERIC_MATCH = re.compile(RE_GENERIC_MATCH.format(color_space=SPACE))

    _gamut = (
        # I think chroma, specifically should be clamped. Generally many
        # some don't to prevent rounding issues. We should only get
        # negative chroma via direct user input, but when translating to
        # Lab, this will be corrected.
        (GamutUnbound(0.0), GamutUnbound(100.0)),
        (GamutUnbound(0.0), GamutUnbound(100.0)),
        (GamutAngle(0.0), GamutAngle(360.0)),
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, Space):
            self.lightness, self.chroma, self.hue = convert.convert(color.coords(), color.space(), self.space())
            self.alpha = color.alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self.lightness, self.chroma, self.hue, self.alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self.lightness = color[0]
            self.chroma = color[1]
            self.hue = color[2]
            self.alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    def _is_achromatic(self, coords):
        """Is achromatic."""

        l, c, h = [util.round_half_up(c, scale=util.DEF_PREC) for c in coords]
        return c < util.ACHROMATIC_THRESHOLD

    def _on_convert(self):
        """
        Run after a convert operation.

        Gives us an opportunity to normalize hues and things like that, if we desire.
        """

        if not (0.0 <= self.hue <= 360.0):
            self.hue = self.hue % 360.0

    def _mix(self, channels1, channels2, factor, factor2=1.0, hue=util.DEF_HUE_ADJ, **kwargs):
        """Blend the color with the given color."""

        hue1 = util.NAN if self._is_achromatic(channels1) else channels1[2]
        hue2 = util.NAN if self._is_achromatic(channels2) else channels2[2]
        return (
            self._mix_channel(channels1[0], channels2[0], factor, factor2),
            self._mix_channel(channels1[1], channels2[1], factor, factor2),
            self._hue_mix_channel(hue1, hue2, factor, factor2, hue=hue)
        )

    @property
    def lightness(self):
        """Lightness."""

        return self._coords[0]

    @lightness.setter
    def lightness(self, value):
        """Get true luminance."""

        self._coords[0] = self.translate_channel(0, value) if isinstance(value, str) else float(value)

    @property
    def chroma(self):
        """Chroma."""

        return self._coords[1]

    @chroma.setter
    def chroma(self, value):
        """chroma."""

        self._coords[1] = self.translate_channel(1, value) if isinstance(value, str) else float(value)

    @property
    def hue(self):
        """Hue."""

        return self._coords[2]

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._coords[2] = self.translate_channel(2, value) if isinstance(value, str) else float(value)

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel in (0, 1):
            return float(value)
        elif channel == 2:
            return parse.norm_deg_channel(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:
            raise ValueError("Unexpected channel index of '{}'".format(channel))

    def to_string(self, *, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs):
        """To string."""

        return self.to_generic_string(alpha=alpha, precision=precision, fit=fit)
