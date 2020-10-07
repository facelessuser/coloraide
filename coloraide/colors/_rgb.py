"""SRGB color class."""
from ._space import Space
from ._gamut import GamutBound
from . import _convert as convert
from . import _parse as parse
from .. import util


class RGB(Space):
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
            self.red, self.green, self.blue = convert.convert(color.coords(), color.space(), self.space())
            self.alpha = color.alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self.red, self.green, self.blue, self.alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self.red = color[0]
            self.green = color[1]
            self.blue = color[2]
            self.alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    def _is_achromatic(self, coords):
        """Is achromatic."""

        r, g, b = [util.round_half_up(c * 255.0) for c in coords]
        return min(r, min(g, b)) == max(r, max(g, b))

    @property
    def red(self):
        """Adjust red."""

        return self._coords[0]

    @red.setter
    def red(self, value):
        """Adjust red."""

        self._coords[0] = self.translate_channel(0, value) if isinstance(value, str) else float(value)

    @property
    def green(self):
        """Adjust green."""

        return self._coords[1]

    @green.setter
    def green(self, value):
        """Adjust green."""

        self._coords[1] = self.translate_channel(1, value) if isinstance(value, str) else float(value)

    @property
    def blue(self):
        """Adjust blue."""

        return self._coords[2]

    @blue.setter
    def blue(self, value):
        """Adjust blue."""

        self._coords[2] = self.translate_channel(2, value) if isinstance(value, str) else float(value)

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if 0 <= channel <= 2:
            return parse.norm_float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:
            raise ValueError("Unexpected channel index of '{}'".format(channel))

    def to_string(self, *, options=None, alpha=None, precision=util.DEF_PREC, fit=None, **kwargs):
        """To string."""

        return super().to_string(alpha=alpha, precision=precision, fit=fit)
