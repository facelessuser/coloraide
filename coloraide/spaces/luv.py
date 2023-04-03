"""
Luv class.

https://en.wikipedia.org/wiki/CIELuv
"""
from __future__ import annotations
from ..spaces import Space, Labish
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT
from .lab import KAPPA, EPSILON, KE, ACHROMATIC_THRESHOLD
from .. import util
from .. import algebra as alg
from ..types import Vector


def xyz_to_luv(xyz: Vector, white: tuple[float, float]) -> Vector:
    """XYZ to Luv."""

    u, v = util.xy_to_uv(util.xyz_to_xyY(xyz, white)[:2])
    w_xyz = util.xy_to_xyz(white)
    ur, vr = util.xy_to_uv(white)

    yr = xyz[1] / w_xyz[1]
    l = 116 * alg.nth_root(yr, 3) - 16 if yr > EPSILON else KAPPA * yr

    return [
        l,
        13 * l * (u - ur),
        13 * l * (v - vr),
    ]


def luv_to_xyz(luv: Vector, white: tuple[float, float]) -> Vector:
    """Luv to XYZ."""

    l, u, v = luv
    w_xyz = util.xy_to_xyz(white)
    ur, vr = util.xy_to_uv(white)

    if l != 0:
        up = (u / (13 * l)) + ur
        vp = (v / (13 * l)) + vr
    else:
        up = vp = 0

    y = w_xyz[1] * (((l + 16) / 116) ** 3 if l > KE else l / KAPPA)

    if vp != 0:
        x = y * ((9 * up) / (4 * vp))
        z = y * ((12 - 3 * up - 20 * vp) / (4 * vp))
    else:
        x = z = 0

    return [x, y, z]


class Luv(Labish, Space):
    """Luv class."""

    BASE = "xyz-d65"
    NAME = "luv"
    SERIALIZE = ("--luv",)
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("u", -215.0, 215.0, flags=FLG_MIRROR_PERCENT),
        Channel("v", -215.0, 215.0, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "lightness": "l"
    }
    WHITE = WHITES['2deg']['D65']

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return coords[0] == 0.0 or alg.rect_to_polar(coords[1], coords[2])[0] < ACHROMATIC_THRESHOLD

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ D50 from Luv."""

        return luv_to_xyz(coords, self.WHITE)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ D50 to Luv."""

        return xyz_to_luv(coords, self.WHITE)
