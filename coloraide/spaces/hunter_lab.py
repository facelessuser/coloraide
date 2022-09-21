"""
Hunter Lab class.

https://support.hunterlab.com/hc/en-us/articles/203997095-Hunter-Lab-Color-Scale-an08-96a2
"""
from __future__ import annotations
from ..cat import WHITES
from ..spaces.lab import Lab
from .. import algebra as alg
from .. import util
from ..types import Vector, VectorLike
from ..channels import Channel, FLG_MIRROR_PERCENT

# Values for the original Hunter Lab with illuminant C.
# Used to calculate an appropriate `Ka` and `Kb` for whatever white point we are using.
CXN = 98.04
CYN = 100.0
CZN = 118.11
CKA = 175.0
CKB = 70.0


def xyz_to_hlab(xyz: Vector, white: VectorLike) -> Vector:
    """Convert XYZ to Hunter Lab."""

    xn, yn, zn = alg.multiply(util.xy_to_xyz(white), 100, dims=alg.D1_SC)
    ka = CKA * alg.nth_root(xn / CXN, 2)
    kb = CKB * alg.nth_root(zn / CZN, 2)
    x, y, z = alg.multiply(xyz, 100, dims=alg.D1_SC)
    l = alg.nth_root(y / yn, 2)
    a = b = 0.0
    if l != 0:
        a = ka * (x / xn - y / yn) / l
        b = kb * (y / yn - z / zn) / l
    return [l * 100, a, b]


def hlab_to_xyz(hlab: Vector, white: VectorLike) -> Vector:
    """Convert Hunter Lab to XYZ."""

    xn, yn, zn = alg.multiply(util.xy_to_xyz(white), 100, dims=alg.D1_SC)
    ka = CKA * alg.nth_root(xn / CXN, 2)
    kb = CKB * alg.nth_root(zn / CZN, 2)
    l, a, b = hlab
    l /= 100
    y = (l ** 2) * yn
    x = (((a * l) / ka) + (y / yn)) * xn
    z = (((b * l) / kb) - (y / yn)) * -zn
    return alg.divide([x, y, z], 100, dims=alg.D1_SC)


class HunterLab(Lab):
    """Hunter Lab class."""

    BASE = 'xyz-d65'
    NAME = "hunter-lab"
    SERIALIZE = ("--hunter-lab",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("a", -210.0, 210.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -210.0, 210.0, flags=FLG_MIRROR_PERCENT)
    )

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Hunter Lab."""

        return hlab_to_xyz(coords, self.white())

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Hunter Lab."""

        return xyz_to_hlab(coords, self.white())
