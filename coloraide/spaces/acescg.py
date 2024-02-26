"""
ACEScg color space.

https://www.oscars.org/science-technology/aces/aces-documentation
"""
from __future__ import annotations
from ..channels import Channel
from ..spaces.srgb_linear import sRGBLinear
from .. import algebra as alg
from ..types import Vector

AP1_TO_XYZ = [
    [0.6624541811085053, 0.13400420645643313, 0.15618768700490782],
    [0.27222871678091454, 0.6740817658111483, 0.05368951740793706],
    [-0.005574649490394108, 0.004060733528982825, 1.0103391003129973]
]

XYZ_TO_AP1 = [
    [1.6410233796943259, -0.32480329418479004, -0.23642469523761225],
    [-0.663662858722983, 1.615331591657338, 0.01675634768553015],
    [0.01172189432837537, -0.008284441996237407, 0.9883948585390213]
]


def acescg_to_xyz(acescg: Vector) -> Vector:
    """Convert ACEScc to XYZ."""

    return alg.matmul(AP1_TO_XYZ, acescg, dims=alg.D2_D1)


def xyz_to_acescg(xyz: Vector) -> Vector:
    """Convert XYZ to ACEScc."""

    return alg.matmul(XYZ_TO_AP1, xyz, dims=alg.D2_D1)


class ACEScg(sRGBLinear):
    """The ACEScg color class."""

    BASE = "xyz-d65"
    NAME = "acescg"
    SERIALIZE = ("--acescg",)  # type: tuple[str, ...]
    WHITE = (0.32168, 0.33767)
    CHANNELS = (
        Channel("r", 0.0, 65504.0, bound=True),
        Channel("g", 0.0, 65504.0, bound=True),
        Channel("b", 0.0, 65504.0, bound=True)
    )
    DYNAMIC_RANGE = 'hdr'

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return acescg_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_to_acescg(coords)
