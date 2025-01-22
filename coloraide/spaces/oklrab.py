"""
Oklrab.

Applies a toe function to Oklab lightness.

> This new lightness estimate closely matches the lightness estimate of CIELab overall and is nearly equal at 50%
> lightness (Y for CIELab L is 0.18406, and  Lr 0.18419) which is useful for compatibility. Worth noting is that it is
> not possible to have a lightness scale that is perfectly uniform independent of viewing conditions and background
> color. This new lightness function is however a better trade-off for cases with a well defined reference white.

https://bottosson.github.io/posts/colorpicker/#intermission---a-new-lightness-estimate-for-oklab
"""
from . oklab import Oklab
from . okhsl import toe, toe_inv
from .. types import Vector


class Oklrab(Oklab):
    """Oklrab."""

    BASE = "oklab"
    NAME = "oklrab"
    SERIALIZE = ("--oklrab",)

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return [toe_inv(coords[0]), coords[1], coords[2]]

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return [toe(coords[0]), coords[1], coords[2]]
