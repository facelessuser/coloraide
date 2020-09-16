"""HWB class."""
from ._base import _Color
from ._tools import _ColorTools, GamutBound, GamutHue
from .. import util
from ..util import parse
from ..util import convert


class _HWB(_ColorTools, _Color):
    """HWB class."""

    SPACE = "hwb"
    DEF_BG = "color(hwb 0 0 0 / 1)"

    _gamut = (
        (GamutHue(0.0), GamutHue(360.0)),
        (GamutBound(0.0), GamutBound(100.0)),
        (GamutBound(0.0), GamutBound(100.0))
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, _Color):
            self._ch, self._cw, self._cb = convert.convert(color._channels, color.space(), self.space())
            self._alpha = color._alpha
        elif isinstance(color, str):
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

    def _is_achromatic(self, channels):
        """Is achromatic."""

        h, w, b = self.coords()
        return (w + b) > (100.0 - util.ACHROMATIC_THRESHOLD)

    @property
    def _ch(self):
        """Hue channel."""

        return self._channels[0]

    @_ch.setter
    def _ch(self, value):
        """Set hue channel."""

        self._channels[0] = value

    @property
    def _cw(self):
        """Whiteness channel."""

        return self._channels[1]

    @_cw.setter
    def _cw(self, value):
        """Set whiteness channel."""

        self._channels[1] = value

    @property
    def _cb(self):
        """Blackness channel."""

        return self._channels[2]

    @_cb.setter
    def _cb(self, value):
        """Set blackness channel."""

        self._channels[2] = value

    def _grayscale(self):
        """Convert to grayscale."""

        factor = 100.0 / (self._cw + self._cb)
        self._cw = self._cw + factor
        self._cb = self._cb + factor

    def _mix(self, channels1, channels2, factor, factor2=1.0):
        """Blend the color with the given color."""

        if self._is_achromatic(channels1):
            channels1[0] = util.NAN
        if self._is_achromatic(channels2):
            channels2[0] = util.NAN
        self._ch = self._hue_mix_channel(channels1[0], channels2[0], factor, factor2)
        self._cw = self._mix_channel(channels1[1], channels2[1], factor, factor2)
        self._cb = self._mix_channel(channels1[2], channels2[2], factor, factor2)

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
            return parse.norm_deg_channel(value)
        elif channel in (1, 2):
            return float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)

    def to_string(self, *, alpha=None, precision=util.DEF_PREC, fit_gamut=False, **kwargs):
        """To string."""

        return self.to_generic_string(alpha=alpha, precision=precision, fit_gamut=fit_gamut)
