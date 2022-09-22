"""Display-p3 color class."""
from __future__ import annotations
from ..cat import WHITES
from .srgb import sRGB, lin_srgb, gam_srgb
from ..types import Vector


class DisplayP3(sRGB):
    """Display-p3 class."""

    BASE = "display-p3-linear"
    NAME = "display-p3"
    WHITE = WHITES['2deg']['D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Display P3."""

        return lin_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Display P3."""

        return gam_srgb(coords)
