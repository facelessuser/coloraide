"""SRGB color class."""
from ._space import Space
from ._tools import Tools, GamutBound
from . import _convert as convert
from . import _parse as parse
from .. import util


class RGB(Tools, Space):
    """SRGB class."""

    _gamut = (
        (GamutBound(0.0), GamutBound(1.0)),
        (GamutBound(0.0), GamutBound(1.0)),
        (GamutBound(0.0), GamutBound(1.0))
    )

    CHANNEL_NAMES = frozenset(["red", "green", "blue", "alpha"])

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, Space):
            self._cr, self._cg, self._cb = convert.convert(color.coords(), color.space(), self.space())
            self._alpha = color._alpha
        elif isinstance(color, str):
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

    def _is_achromatic(self, coords):
        """Is achromatic."""

        r, g, b = [util.round_half_up(c * 255.0) for c in coords]
        return min(r, min(g, b)) == max(r, max(g, b))

    @property
    def _cr(self):
        """Red channel."""

        return self._coords[0]

    @_cr.setter
    def _cr(self, value):
        """Set red channel."""

        self._coords[0] = value

    @property
    def _cg(self):
        """Green channel."""

        return self._coords[1]

    @_cg.setter
    def _cg(self, value):
        """Set green channel."""

        self._coords[1] = value

    @property
    def _cb(self):
        """Blue channel."""

        return self._coords[2]

    @_cb.setter
    def _cb(self, value):
        """Set blue channel."""

        self._coords[2] = value

    def _mix(self, channels1, channels2, factor, factor2=1.0, **kwargs):
        """Blend the color with the given color."""

        return (
            self._mix_channel(channels1[0], channels2[0], factor, factor2),
            self._mix_channel(channels1[1], channels2[1], factor, factor2),
            self._mix_channel(channels1[2], channels2[2], factor, factor2)
        )

    @property
    def red(self):
        """Adjust red."""

        return self._cr

    @red.setter
    def red(self, value):
        """Adjust red."""

        self._cr = self.translate_channel(0, value) if isinstance(value, str) else float(value)

    @property
    def green(self):
        """Adjust green."""

        return self._cg

    @green.setter
    def green(self, value):
        """Adjust green."""

        self._cg = self.translate_channel(1, value) if isinstance(value, str) else float(value)

    @property
    def blue(self):
        """Adjust blue."""

        return self._cb

    @blue.setter
    def blue(self, value):
        """Adjust blue."""

        self._cb = self.translate_channel(2, value) if isinstance(value, str) else float(value)

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        return float(value) if channel > 0 else parse.norm_alpha_channel(value)

    def to_string(self, *, options=None, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs):
        """To string."""

        return self.to_generic_string(alpha=alpha, precision=precision, fit=fit)
