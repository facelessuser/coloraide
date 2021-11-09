"""XYZ D65 class."""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound
import re
from ..util import Vector, MutableVector
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class XYZ(Space):
    """XYZ D65 class."""

    SPACE = "xyz"
    SERIALIZE = ("xyz", "xyz-d65")  # type: Tuple[str, ...]
    CHANNEL_NAMES = ("x", "y", "z", "alpha")
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
    def _to_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, xyz)

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """From XYZ."""

        return parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz)
