"""Display-p3 color class."""
from ..cat import WHITES
from .srgb import SRGB, lin_srgb, gam_srgb
from ..types import Vector


class DisplayP3(SRGB):
    """Display-p3 class."""

    BASE = "display-p3-linear"
    NAME = "display-p3"
    WHITE = WHITES['2deg']['D65']

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To XYZ from Display P3."""

        return lin_srgb(coords)

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From XYZ to Display P3."""

        return gam_srgb(coords)
