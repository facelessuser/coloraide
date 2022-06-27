"""XYZ D65 class."""
from ..spaces import Space
from ..cat import WHITES
from ..gamut.bounds import GamutUnbound
from ..types import Vector
from typing import Tuple


class XYZD65(Space):
    """XYZ D65 class."""

    BASE = "xyz-d65"
    NAME = "xyz-d65"
    SERIALIZE = ("xyz-d65", 'xyz')  # type: Tuple[str, ...]
    CHANNEL_NAMES = ("x", "y", "z")
    WHITE = WHITES['2deg']['D65']

    BOUNDS = (
        GamutUnbound(0.0, 1.0),
        GamutUnbound(0.0, 1.0),
        GamutUnbound(0.0, 1.0)
    )

    @classmethod
    def x(cls, value: float) -> float:
        """Shift the X."""

        return value

    @classmethod
    def y(cls, value: float) -> float:
        """Set Y."""

        return value

    @classmethod
    def z(cls, value: float) -> float:
        """Set Z channel."""

        return value

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """
        To XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """
        From XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords
