"""LCH class."""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, Cylindrical, Angle, Percent
from .luv import Luv
from .. import util
import re
import math

ACHROMATIC_THRESHOLD = 0.000000000002


def luv_to_lchuv(luv):
    """Luv to Lch(uv)."""

    l, u, v = luv

    c = math.sqrt(u ** 2 + v ** 2)
    h = math.degrees(math.atan2(v, u))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = util.NaN

    return [l, c, util.constrain_hue(h)]


def lchuv_to_luv(lchuv):
    """Lch(uv) to Luv."""

    l, c, h = lchuv
    h = util.no_nan(h)

    # If, for whatever reason (mainly direct user input),
    # if chroma is less than zero, clamp to zero.
    if c < 0.0:
        c = 0.0

    return (
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    )


class Lchuv(Cylindrical, Space):
    """Lch(uv) class."""

    SPACE = "lchuv"
    SERIALIZE = ("--lchuv",)
    CHANNEL_NAMES = ("lightness", "chroma", "hue", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    RANGE = (
        GamutUnbound([Percent(0), Percent(100.0)]),
        GamutUnbound([0.0, 176.0]),
        GamutUnbound([Angle(0.0), Angle(360.0)]),
    )

    @property
    def lightness(self):
        """Lightness."""

        return self._coords[0]

    @lightness.setter
    def lightness(self, value):
        """Get true luminance."""

        self._coords[0] = self._handle_input(value)

    @property
    def chroma(self):
        """Chroma."""

        return self._coords[1]

    @chroma.setter
    def chroma(self, value):
        """chroma."""

        self._coords[1] = self._handle_input(value)

    @property
    def hue(self):
        """Hue."""

        return self._coords[2]

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def null_adjust(cls, coords, alpha):
        """On color update."""

        if coords[1] < ACHROMATIC_THRESHOLD:
            coords[2] = util.NaN
        return coords, alpha

    @classmethod
    def _to_luv(cls, parent, lchuv):
        """To Luv."""

        return lchuv_to_luv(lchuv)

    @classmethod
    def _from_luv(cls, parent, luv):
        """To Luv."""

        return luv_to_lchuv(luv)

    @classmethod
    def _to_xyz(cls, parent, lchuv):
        """To XYZ."""

        return Luv._to_xyz(parent, cls._to_luv(parent, lchuv))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return cls._from_luv(parent, Luv._from_xyz(parent, xyz))
