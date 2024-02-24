"""
Lab class.

https://ia802802.us.archive.org/23/items/gov.law.cie.15.2004/cie.15.2004.pdf
http://www.brucelindbloom.com/Eqn_Lab_to_XYZ.html
"""
from __future__ import annotations
from ...spaces import Space, Labish
from ...cat import WHITES
from ...channels import Channel, FLG_MIRROR_PERCENT
from ... import util
from ... import algebra as alg
from ...types import VectorLike, Vector

ACHROMATIC_THRESHOLD = 1e-4
EPSILON = 216 / 24389  # `6^3 / 29^3`
EPSILON3 = 6 / 29  # Cube root of EPSILON
KAPPA = 24389 / 27
KE = 8  # KAPPA * EPSILON = 8


def lab_to_xyz(lab: Vector, white: VectorLike) -> Vector:
    """Convert CIE Lab to XYZ using the reference white."""

    l, a, b = lab

    # compute `f`, starting with the luminance-related term
    fy = (l + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200

    # compute `xyz`
    xyz = [
        fx ** 3 if fx > EPSILON3 else (116 * fx - 16) / KAPPA,
        fy ** 3 if l > KE else l / KAPPA,
        fz ** 3 if fz > EPSILON3 else (116 * fz - 16) / KAPPA
    ]

    # Compute XYZ by scaling `xyz` by reference `white`
    return alg.multiply(xyz, white, dims=alg.D1)


def xyz_to_lab(xyz: Vector, white: VectorLike) -> Vector:
    """Convert XYZ to CIE Lab using the reference white."""

    # compute `xyz`, which is XYZ scaled relative to reference white
    xyz = alg.divide(xyz, white, dims=alg.D1)
    # Compute `fx`, `fy`, and `fz`
    fx, fy, fz = [alg.nth_root(i, 3) if i > EPSILON else (KAPPA * i + 16) / 116 for i in xyz]

    return [
        (116.0 * fy) - 16.0,
        500.0 * (fx - fy),
        200.0 * (fy - fz)
    ]


class Lab(Labish, Space):
    """Lab class."""

    CHANNELS = (
        Channel("l", 0.0, 1.0),
        Channel("a", 1.0, 1.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", 1.0, 1.0, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "lightness": "l"
    }

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return alg.rect_to_polar(coords[1], coords[2])[0] < ACHROMATIC_THRESHOLD

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ D50 from Lab."""

        return lab_to_xyz(coords, util.xy_to_xyz(self.white()))

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ D50 to Lab."""

        return xyz_to_lab(coords, util.xy_to_xyz(self.white()))


class CIELab(Lab):
    """CIE Lab D50."""

    BASE = "xyz-d50"
    NAME = "lab"
    SERIALIZE = ("--lab",)
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("a", -125.0, 125.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -125.0, 125.0, flags=FLG_MIRROR_PERCENT)
    )
    WHITE = WHITES['2deg']['D50']
