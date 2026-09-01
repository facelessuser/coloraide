"""
ACES 2065-1 color space.

https://www.oscars.org/science-technology/aces/aces-documentation
"""
from __future__ import annotations
from ..channels import Channel
from .srgb_linear import RGB
from .. import algebra as alg
from ..cat import WHITES
from ..types import Vector

AP0_TO_XYZ = [
    [ 9.5255239593818570e-01,  0.0000000000000000e+00,  9.3678631660468550e-05],
    [ 3.4396644976507507e-01,  7.2816609661348570e-01, -7.2132546378560790e-02],
    [ 0.0000000000000000e+00,  0.0000000000000000e+00,  1.0088251843515859e+00]
]

XYZ_TO_AP0 = [
    [ 1.0498110174979742e+00,  0.0000000000000000e+00, -9.7484540579252870e-05],
    [-4.9590302307731976e-01,  1.3733130458157063e+00,  9.8240036057309990e-02],
    [ 0.0000000000000000e+00,  0.0000000000000000e+00,  9.9125201820049900e-01]
]

MIN = 0.0
MAX = 1.0


def aces_to_xyz(aces: Vector) -> Vector:
    """Convert ACEScc to XYZ."""

    return alg.matmul_x3(AP0_TO_XYZ, aces, dims=alg.D2_D1)


def xyz_to_aces(xyz: Vector) -> Vector:
    """Convert XYZ to ACEScc."""

    return alg.matmul_x3(XYZ_TO_AP0, xyz, dims=alg.D2_D1)


class ACES20651(RGB):
    """The ACES color class."""

    BASE = "xyz-d65"
    NAME = "aces2065-1"
    SERIALIZE = ("--aces2065-1",)
    WHITE = WHITES['2deg']['ACES-D60']
    CHANNELS = (
        Channel("r", 0.0, 65504.0, bound=True),
        Channel("g", 0.0, 65504.0, bound=True),
        Channel("b", 0.0, 65504.0, bound=True)
    )
    DYNAMIC_RANGE = 'hdr'
    TO_XYZ = AP0_TO_XYZ
    TO_RGB = XYZ_TO_AP0

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return aces_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_to_aces(coords)
