"""
RLAB.

https://scholarworks.rit.edu/cgi/viewcontent.cgi?article=1153&context=article
https://www.imaging.org/site/PDFS/Papers/1997/RP-0-67/2368.pdf
"""
from __future__ import annotations
from ..cat import WHITES
from ..spaces.lab import Lab
from .. import algebra as alg
from ..types import Vector
from ..channels import Channel, FLG_MIRROR_PERCENT

XYZ_TO_XYZ_REF = [
    [1.0521266389510715, 2.220446049250313e-16, 0.0],
    [0.0, 1.0, 2.414043899674756e-19],
    [0.0, 0.0, 0.9182249511582473]
]

XYZ_REF_TO_XYZ = [
    [0.9504559270516716, -2.110436108208428e-16, 5.548406636355788e-35],
    [0.0, 1.0, -2.629033219615395e-19],
    [0.0, 0.0, 1.0890577507598784]
]

EXP = 2.3


def rlab_to_xyz(rlab: Vector) -> Vector:
    """RLAB to XYZ."""

    l, a, b = rlab
    yr = l / 100
    xr = alg.npow((a / 430) + yr, EXP)
    zr = alg.npow(yr - (b / 170), EXP)
    return alg.dot(XYZ_REF_TO_XYZ, [xr, alg.npow(yr, EXP), zr], dims=alg.D2_D1)


def xyz_to_rlab(xyz: Vector) -> Vector:
    """XYZ to RLAB."""

    xyz_ref = alg.dot(XYZ_TO_XYZ_REF, xyz, dims=alg.D2_D1)
    xr, yr, zr = [alg.nth_root(c, EXP) for c in xyz_ref]
    l = 100 * yr
    a = 430 * (xr - yr)
    b = 170 * (yr - zr)
    return [l, a, b]


class RLAB(Lab):
    """RLAB class."""

    BASE = 'xyz-d65'
    NAME = "rlab"
    SERIALIZE = ("--rlab",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("a", -125.0, 125.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -125.0, 125.0, flags=FLG_MIRROR_PERCENT)
    )

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Hunter Lab."""

        return rlab_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Hunter Lab."""

        return xyz_to_rlab(coords)
