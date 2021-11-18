"""XYZ D65 class."""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound
import re
from ..util import MutableVector
from typing import Tuple


class XYZ(Space):
    """XYZ D65 class."""

    BASE = "xyz"
    NAME = "xyz"
    SERIALIZE = ("xyz", "xyz-d65")  # type: Tuple[str, ...]
    CHANNEL_NAMES = ("x", "y", "z")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    BOUNDS = (
        GamutUnbound(0.0, 1.0),
        GamutUnbound(0.0, 1.0),
        GamutUnbound(0.0, 1.0)
    )

    @property
    def x(self) -> float:
        """X channel."""

        return self._coords[0]

    @x.setter
    def x(self, value: float) -> None:
        """Shift the X."""

        self._coords[0] = self._handle_input(value)

    @property
    def y(self) -> float:
        """Y channel."""

        return self._coords[1]

    @y.setter
    def y(self, value: float) -> None:
        """Set Y."""

        self._coords[1] = self._handle_input(value)

    @property
    def z(self) -> float:
        """Z channel."""

        return self._coords[2]

    @z.setter
    def z(self, value: float) -> None:
        """Set Z channel."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def to_base(cls, coords: MutableVector) -> MutableVector:
        """
        To XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords

    @classmethod
    def from_base(cls, coords: MutableVector) -> MutableVector:
        """
        From XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords
