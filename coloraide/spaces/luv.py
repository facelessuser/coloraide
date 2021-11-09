"""
Luv class.

https://en.wikipedia.org/wiki/CIELUV
"""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, FLG_PERCENT, WHITES, Labish
from .lab.base import KAPPA, EPSILON, KE
from .xyz import XYZ
from .. import util
import re
from ..util import Vector, MutableVector
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def xyz_to_luv(xyz: Vector, white: str) -> MutableVector:
    """XYZ to Luv."""

    u, v = util.xyz_to_uv(xyz)
    w_xyz = util.xy_to_xyz(WHITES[white])
    ur, vr = util.xyz_to_uv(w_xyz)

    yr = xyz[1] / w_xyz[1]
    l = 116 * util.nth_root(yr, 3) - 16 if yr > EPSILON else KAPPA * yr

    return [
        l,
        13 * l * (u - ur),
        13 * l * (v - vr),
    ]


def luv_to_xyz(luv: Vector, white: str) -> MutableVector:
    """Luv to XYZ."""

    l, u, v = luv
    xyz = util.xy_to_xyz(WHITES[white])
    ur, vr = util.xyz_to_uv(xyz)

    if l != 0:
        up = (u / (13 * l)) + ur
        vp = (v / (13 * l)) + vr
    else:
        up = vp = 0

    y = xyz[1] * (((l + 16) / 116) ** 3 if l > KE else l / KAPPA)

    if vp != 0:
        x = y * ((9 * up) / (4 * vp))
        z = y * ((12 - 3 * up - 20 * vp) / (4 * vp))
    else:
        x = z = 0

    return [x, y, z]


class Luv(Labish, Space):
    """Oklab class."""

    SPACE = "luv"
    SERIALIZE = ("--luv",)
    CHANNEL_NAMES = ("l", "u", "v", "alpha")
    CHANNEL_ALIASES = {
        "lightness": "l"
    }
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D50"

    BOUNDS = (
        GamutUnbound(0.0, 100.0, FLG_PERCENT),
        GamutUnbound(-175.0, 175.0),
        GamutUnbound(-175.0, 175.0)
    )

    @property
    def l(self) -> float:
        """L channel."""

        return self._coords[0]

    @l.setter
    def l(self, value: float) -> None:
        """Get true luminance."""

        self._coords[0] = self._handle_input(value)

    @property
    def u(self) -> float:
        """U channel."""

        return self._coords[1]

    @u.setter
    def u(self, value: float) -> None:
        """U axis."""

        self._coords[1] = self._handle_input(value)

    @property
    def v(self) -> float:
        """V channel."""

        return self._coords[2]

    @v.setter
    def v(self, value: float) -> None:
        """V axis."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def _to_xyz(cls, parent: 'Color', luv: Vector) -> MutableVector:
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, luv_to_xyz(luv, cls.WHITE))

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """From XYZ."""

        return xyz_to_luv(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz), cls.WHITE)
