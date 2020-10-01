"""XYZ class."""
from ._space import Space, RE_GENERIC_MATCH
from ._gamut import GamutUnbound
from . import _convert as convert
from . import _parse as parse
from .. import util
import re


class XYZ(Space):
    """XYZ class."""

    SPACE = "xyz"
    DEF_BG = "color(xyz 0 0 0 / 1)"
    CHANNEL_NAMES = frozenset(["x", "y", "z", "alpha"])
    GENERIC_MATCH = re.compile(RE_GENERIC_MATCH.format(color_space=SPACE))

    _gamut = (
        (GamutUnbound(0.0), GamutUnbound(1.0)),
        (GamutUnbound(0.0), GamutUnbound(1.0)),
        (GamutUnbound(0.0), GamutUnbound(1.0))
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, Space):
            self.x, self.y, self.z = convert.convert(color.coords(), color.space(), self.space())
            self.alpha = color.alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self.x, self.y, self.z, self.alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self.x = color[0]
            self.y = color[1]
            self.z = color[2]
            self.alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    def _is_achromatic(self, coords):
        """Is achromatic."""

        points = [util.round_half_up(c) for c in util.divide(coords, convert.D50_REF_WHITE)]
        mn = min(min(points[0], points[1]), points[2])
        mx = max(max(points[0], points[1]), points[2])
        return mn == mx

    def _mix(self, channels1, channels2, factor, factor2=1.0, **kwargs):
        """Blend the color with the given color."""

        return (
            self._mix_channel(channels1[0], channels2[0], factor, factor2),
            self._mix_channel(channels1[1], channels2[1], factor, factor2),
            self._mix_channel(channels1[2], channels2[2], factor, factor2)
        )

    @property
    def x(self):
        """X channel."""

        return self._coords[0]

    @x.setter
    def x(self, value):
        """Shift the X."""

        self._coords[0] = float(value)

    @property
    def y(self):
        """Y channel."""

        return self._coords[1]

    @y.setter
    def y(self, value):
        """Set Y."""

        self._coords[1] = float(value)

    @property
    def z(self):
        """Z channel."""

        return self._coords[2]

    @z.setter
    def z(self, value):
        """Set Z channel."""

        self._coords[2] = float(value)

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel in (0, 1, 2):
            return float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:
            raise ValueError("Unexpected channel index of '{}'".format(channel))

    def to_string(self, *, options=None, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs):
        """To string."""

        return super().to_string(alpha=alpha, precision=precision, fit=fit)
