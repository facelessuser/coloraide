"""XYZ D65 class."""
from __future__ import annotations
from ..spaces import Space
from ..cat import WHITES
from ..channels import Channel
from ..types import Vector


class XYZD65(Space):
    """XYZ D65 class."""

    BASE = "xyz-d65"
    NAME = "xyz-d65"
    SERIALIZE = ("xyz-d65", 'xyz')  # type: tuple[str, ...]
    CHANNELS = (
        Channel("x", 0.0, 1.0),
        Channel("y", 0.0, 1.0),
        Channel("z", 0.0, 1.0)
    )
    WHITE = WHITES['2deg']['D65']

    def to_base(self, coords: Vector) -> Vector:
        """
        To XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords

    def from_base(self, coords: Vector) -> Vector:
        """
        From XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords
