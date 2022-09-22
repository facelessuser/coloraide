"""
ACES 2065-1 color space.

https://www.oscars.org/science-technology/aces/aces-documentation
"""
from __future__ import annotations
from ..channels import Channel
from ..spaces.srgb import sRGB
from .. import algebra as alg
from ..types import Vector

AP0_TO_XYZ = [
    [0.9525523959381857, 0.0, 9.367863166046855e-05],
    [0.34396644976507507, 0.7281660966134857, -0.07213254637856079],
    [0.0, 0.0, 1.0088251843515859]
]

XYZ_TO_AP0 = [
    [1.0498110174979742, 0.0, -9.748454057925287e-05],
    [-0.49590302307731976, 1.3733130458157063, 0.09824003605730998],
    [0.0, 0.0, 0.991252018200499]
]

MIN = 0.0
MAX = 1.0


def aces_to_xyz(aces: Vector) -> Vector:
    """Convert ACEScc to XYZ."""

    return alg.dot(AP0_TO_XYZ, aces, dims=alg.D2_D1)


def xyz_to_aces(xyz: Vector) -> Vector:
    """Convert XYZ to ACEScc."""

    return alg.dot(XYZ_TO_AP0, xyz, dims=alg.D2_D1)


class ACES20651(sRGB):
    """The ACES color class."""

    BASE = "xyz-d65"
    NAME = "aces2065-1"
    SERIALIZE = ("--aces2065-1",)  # type: tuple[str, ...]
    WHITE = (0.32168, 0.33767)
    CHANNELS = (
        Channel("r", 0.0, 65504.0, bound=True),
        Channel("g", 0.0, 65504.0, bound=True),
        Channel("b", 0.0, 65504.0, bound=True)
    )
    DYNAMIC_RANGE = 'hdr'

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return aces_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_to_aces(coords)
