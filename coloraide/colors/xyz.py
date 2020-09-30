"""XYZ class."""
from ._space import Space, RE_GENERIC_MATCH
from ._tools import Tools, GamutUnbound
from . import _convert as convert
from . import _parse as parse
from .. import util
import re


class XYZ(Tools, Space):
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
            self._cx, self._cy, self._cz = convert.convert(color.coords(), color.space(), self.space())
            self._alpha = color._alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._cx, self._cy, self._cz, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._cx = color[0]
            self._cy = color[1]
            self._cz = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    def _is_achromatic(self, coords):
        """Is achromatic."""

        points = [util.round_half_up(c) for c in util.divide(coords, convert.D50_REF_WHITE)]
        mn = min(min(points[0], points[1]), points[2])
        mx = max(max(points[0], points[1]), points[2])
        return mn == mx

    @property
    def _cx(self):
        """X channel."""

        return self._coords[0]

    @_cx.setter
    def _cx(self, value):
        """Set X channel."""

        self._coords[0] = value

    @property
    def _cy(self):
        """Y channel."""

        return self._coords[1]

    @_cy.setter
    def _cy(self, value):
        """Set Y channel."""

        self._coords[1] = value

    @property
    def _cz(self):
        """Z channel."""

        return self._coords[2]

    @_cz.setter
    def _cz(self, value):
        """Set Z channel."""

        self._coords[2] = value

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

        return self._cx

    @x.setter
    def x(self, value):
        """Shift the X."""

        self._cx = float(value)

    @property
    def y(self):
        """Y channel."""

        return self._cy

    @y.setter
    def y(self, value):
        """Set Y."""

        self._cy = float(value)

    @property
    def z(self):
        """Z channel."""

        return self._cz

    @z.setter
    def z(self, value):
        """Set Z channel."""

        self._cz = float(value)

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel in (0, 2):
            return float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)

    def to_string(self, *, options=None, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs):
        """To string."""

        return self.to_generic_string(alpha=alpha, precision=precision, fit=fit)
