"""A98 RGB color class."""
from __future__ import annotations
from .srgb_linear import sRGBLinear
from .. import algebra as alg
from ..types import Vector


def lin_a98rgb(rgb: Vector) -> Vector:
    """Convert an array of a98-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return [alg.npow(val, 563 / 256) for val in rgb]


def gam_a98rgb(rgb: Vector) -> Vector:
    """Convert an array of linear-light a98-rgb  in the range 0.0-1.0 to gamma corrected form."""

    return [alg.npow(val, 256 / 563) for val in rgb]


class A98RGB(sRGBLinear):
    """A98 RGB class."""

    BASE = "a98-rgb-linear"
    NAME = "a98-rgb"

    def linear(self) -> str:
        """Return linear version of the RGB (if available)."""

        return self.BASE

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from A98 RGB."""

        return lin_a98rgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to A98 RGB."""

        return gam_a98rgb(coords)
