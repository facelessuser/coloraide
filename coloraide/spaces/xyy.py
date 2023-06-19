"""
The xyY color space.

https://en.wikipedia.org/wiki/CIE_1931_color_space#CIE_xy_chromaticity_diagram_and_the_CIE_xyY_color_space
"""
from __future__ import annotations
from ..spaces import Space
from ..channels import Channel
from ..cat import WHITES
from .. import util
from ..types import Vector
from .. import algebra as alg
import math


class xyY(Space):
    """The xyY class."""

    BASE = "xyz-d65"
    NAME = "xyy"
    SERIALIZE = ("--xyy",)
    CHANNELS = (
        Channel("x", 0.0, 1.0),
        Channel("y", 0.0, 1.0),
        Channel("Y", 0.0, 1.0)
    )
    WHITE = WHITES['2deg']['D65']

    def is_achromatic(self, coords: Vector) -> bool:
        """Test if color is achromatic."""

        if math.isclose(0.0, coords[-1], abs_tol=1e-4):
            return True

        for x in alg.vcross(coords[:-1], self.WHITE):
            if not math.isclose(0.0, x, abs_tol=1e-6):
                return False
        return True

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return util.xy_to_xyz(coords[0:2], coords[2])

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return util.xyz_to_xyY(coords, self.white())
