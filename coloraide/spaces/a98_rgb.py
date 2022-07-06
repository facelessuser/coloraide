"""A98 RGB color class."""
from ..cat import WHITES
from .srgb import SRGB
from .. import algebra as alg
from ..types import Vector


def lin_a98rgb(rgb: Vector) -> Vector:
    """Convert an array of a98-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return [alg.npow(val, 563 / 256) for val in rgb]


def gam_a98rgb(rgb: Vector) -> Vector:
    """Convert an array of linear-light a98-rgb  in the range 0.0-1.0 to gamma corrected form."""

    return [alg.npow(val, 256 / 563) for val in rgb]


class A98RGB(SRGB):
    """A98 RGB class."""

    BASE = "a98-rgb-linear"
    NAME = "a98-rgb"
    WHITE = WHITES['2deg']['D65']

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To XYZ from A98 RGB."""

        return lin_a98rgb(coords)

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From XYZ to A98 RGB."""

        return gam_a98rgb(coords)
