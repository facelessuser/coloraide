"""
Luv class.

https://en.wikipedia.org/wiki/CIELUV
"""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, Percent, WHITES
from .xyz import XYZ
from .. import util
import re


def xyz_to_uv(xyz):
    """XYZ to UV."""

    x, y, z = xyz
    denom = (x + 15 * y + 3 * z)
    if denom != 0:
        u = (4 * x) / (x + 15 * y + 3 * z)
        v = (9 * y) / (x + 15 * y + 3 * z)
    else:
        u = v = 0

    return u, v


def xyz_to_luv(xyz, white):
    """XYZ to Luv."""

    u, v = xyz_to_uv(xyz)
    un, vn = xyz_to_uv(WHITES[white])

    y = xyz[1] / WHITES[white][1]
    l = 116 * util.nth_root(y, 3) - 16 if y > ((6 / 29) ** 3) else ((29 / 3) ** 3) * y

    return [
        l,
        13 * l * (u - un),
        13 * l * (v - vn),
    ]


def luv_to_xyz(luv, white):
    """Luv to XYZ."""

    l, u, v = luv
    un, vn = xyz_to_uv(WHITES[white])

    if l != 0:
        up = (u / ( 13 * l)) + un
        vp = (v / ( 13 * l)) + vn
    else:
        up = vp = 0

    y = WHITES[white][1] * ((l + 16) / 116) ** 3 if l > 8 else WHITES[white][1] * l * ((3 / 29) ** 3)

    if vp != 0:
        x = y * ((9 * up) / (4 * vp))
        z = y * ((12 - 3 * up - 20 * vp) / (4 * vp))
    else:
        x = z = 0

    return [x, y, z]


class Luv(Space):
    """Oklab class."""

    SPACE = "luv"
    SERIALIZE = ("--luv",)
    CHANNEL_NAMES = ("lightness", "u", "v", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    RANGE = (
        GamutUnbound([Percent(0), Percent(100.0)]),
        GamutUnbound([-175.0, 175.0]),
        GamutUnbound([-175.0, 175.0])
    )

    @property
    def lightness(self):
        """L channel."""

        return self._coords[0]

    @lightness.setter
    def lightness(self, value):
        """Get true luminance."""

        self._coords[0] = self._handle_input(value)

    @property
    def u(self):
        """U channel."""

        return self._coords[1]

    @u.setter
    def u(self, value):
        """U axis."""

        self._coords[1] = self._handle_input(value)

    @property
    def v(self):
        """V channel."""

        return self._coords[2]

    @v.setter
    def v(self, value):
        """V axis."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def _to_xyz(cls, parent, luv):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, luv_to_xyz(luv, cls.WHITE))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return xyz_to_luv(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz), cls.WHITE)
