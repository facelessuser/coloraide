"""LCH class."""
from ._space import Space, RE_GENERIC_MATCH
from ._tools import Tools, GamutUnbound, GamutAngle
from . import _convert as convert
from . import _parse as parse
from .. import util
import re


class LCH(Tools, Space):
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
            self._cl, self._cc, self._ch = convert.convert(color.coords(), color.space(), self.space())
            self._alpha = color._alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._cl, self._cc, self._ch, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._cl = color[0]
            self._cc = color[1]
            self._ch = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
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

        if not (0.0 <= self._ch <= 360.0):
            self._ch = self._ch % 360.0

    @property
    def _cl(self):
        """Lightness channel."""

        return self._coords[0]

    @_cl.setter
    def _cl(self, value):
        """
        Set lightness channel.

        Theoretically, there is no upper bound here. HDR may use much higher.

        TODO: Do we clamp the higher end or not?
        """

        self._coords[0] = value

    @property
    def _cc(self):
        """Chroma channel."""

        return self._coords[1]

    @_cc.setter
    def _cc(self, value):
        """
        Set chroma channel.

        Theoretically, there is no upper bound here. Useful range is probably below 230,
        but visible range in most settings is probably less.

        TODO: Do we clamp the higher end or not?
        """

        self._coords[1] = value

    @property
    def _ch(self):
        """Hue channel."""

        return self._coords[2]

    @_ch.setter
    def _ch(self, value):
        """Set B on LAB axis."""

        self._coords[2] = value

    def _mix(self, channels1, channels2, factor, factor2=1.0):
        """Blend the color with the given color."""

        hue1 = util.NAN if self._is_achromatic(channels1) else channels1[2]
        hue2 = util.NAN if self._is_achromatic(channels2) else channels2[2]
        return (
            self._mix_channel(channels1[0], channels2[0], factor, factor2),
            self._mix_channel(channels1[1], channels2[1], factor, factor2),
            self._hue_mix_channel(hue1, hue2, factor, factor2)
        )

    @property
    def lightness(self):
        """Lightness."""

        return self._cl

    @lightness.setter
    def lightness(self, value):
        """Get true luminance."""

        self._cl = self.tx_channel(0, value) if isinstance(value, str) else float(value)

    @property
    def chroma(self):
        """Chroma."""

        return self._cc

    @chroma.setter
    def chroma(self, value):
        """chroma."""

        self._cc = self.tx_channel(1, value) if isinstance(value, str) else float(value)

    @property
    def hue(self):
        """Hue."""

        return self._ch

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._ch = self.tx_channel(2, value) if isinstance(value, str) else float(value)

    @classmethod
    def tx_channel(cls, channel, value):
        """Translate channel string."""

        if channel in (1, 0):
            return float(value)
        elif channel == 2:
            return parse.norm_deg_channel(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)

    def to_string(self, *, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs):
        """To string."""

        return self.to_generic_string(alpha=alpha, precision=precision, fit=fit)
