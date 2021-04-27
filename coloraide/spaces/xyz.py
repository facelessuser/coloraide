"""XYZ class."""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound
from . import _cat
import re


class XYZ(Space):
    """XYZ class."""

    SPACE = "xyz"
    CHANNEL_NAMES = ("x", "y", "z", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = _cat.WHITES["D50"]

    RANGE = (
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0])
    )

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
