"""XYZ class."""
from ._space import Space, RE_DEFAULT_MATCH
from ._gamut import GamutUnbound
from . import _convert as convert
import re


class XYZ(Space):
    """XYZ class."""

    SPACE = "xyz"
    DEF_VALUE = "color(xyz 0 0 0 / 1)"
    CHANNEL_NAMES = ("x", "y", "z", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D50"]

    _range = (
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0])
    )

    def __init__(self, color=DEF_VALUE):
        """Initialize."""

        super().__init__(color)

    @property
    def x(self):
        """X channel."""

        return self._coords[0]

    @x.setter
    def x(self, value):
        """Shift the X."""

        self._coords[0] = self._handle_input(value)

    @property
    def y(self):
        """Y channel."""

        return self._coords[1]

    @y.setter
    def y(self, value):
        """Set Y."""

        self._coords[1] = self._handle_input(value)

    @property
    def z(self):
        """Z channel."""

        return self._coords[2]

    @z.setter
    def z(self, value):
        """Set Z channel."""

        self._coords[2] = self._handle_input(value)
