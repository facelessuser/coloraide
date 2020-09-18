"""LCH class."""
from ._base import _Color
from ._tools import _ColorTools, GamutUnbound, GamutAngle, GamutBound
from .. import util
from ..util import parse
from ..util import convert


class _LCH(_ColorTools, _Color):
    """LCH class."""

    SPACE = "lch"
    DEF_BG = "color(lch 0 0 0 / 1)"

    _gamut = (
        (GamutBound(0.0), GamutUnbound(100.0)),  # Technically we could/should clamp the zero side.
        (GamutBound(0.0), GamutUnbound(100.0)),  # Again, I think chroma should be clamped on the zero side.
        (GamutAngle(0.0), GamutAngle(360.0)),
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, _Color):
            self._cl, self._cc, self._ch = convert.convert(color._channels, color.space(), self.space())
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

    def _is_achromatic(self, channels):
        """Is achromatic."""

        l, c, h = self.coords()
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

        return self._channels[0]

    @_cl.setter
    def _cl(self, value):
        """
        Set lightness channel.

        Theoretically, there is no upper bound here. HDR may use much higher.

        TODO: Do we clamp the higher end or not?
        """

        self._channels[0] = value

    @property
    def _cc(self):
        """Chroma channel."""

        return self._channels[1]

    @_cc.setter
    def _cc(self, value):
        """
        Set chroma channel.

        Theoretically, there is no upper bound here. Useful range is probably below 230,
        but visible range in most settings is probably less.

        TODO: Do we clamp the higher end or not?
        """

        self._channels[1] = value

    @property
    def _ch(self):
        """Hue channel."""

        return self._channels[2]

    @_ch.setter
    def _ch(self, value):
        """Set B on LAB axis."""

        self._channels[2] = value

    def _grayscale(self):
        """Convert to grayscale."""

        self._cc = 0

    def _mix(self, channels1, channels2, factor, factor2=1.0):
        """Blend the color with the given color."""

        if self._is_achromatic(channels1):
            channels1[2] = util.NAN
        if self._is_achromatic(channels2):
            channels2[2] = util.NAN
        self._cl = self._mix_channel(channels1[0], channels2[0], factor, factor2)
        self._cc = self._mix_channel(channels1[1], channels2[1], factor, factor2)
        self._ch = self._hue_mix_channel(channels1[2], channels2[2], factor, factor2)

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
