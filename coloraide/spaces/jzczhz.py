"""
JzCzhz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, Cylindrical, Angle
from . import _cat
from .jzazbz import Jzazbz
from .. import util
import re
import math

ACHROMATIC_THRESHOLD = 0.0002


def jzazbz_to_jzczhz(jzazbz):
    """Jzazbz to JzCzhz."""

    jz, az, bz = jzazbz

    cz = math.sqrt(az ** 2 + bz ** 2)
    hz = math.degrees(math.atan2(bz, az))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if cz < ACHROMATIC_THRESHOLD:
        hz = util.NaN

    return [jz, cz, util.constrain_hue(hz)]


def jzczhz_to_jzazbz(jzczhz):
    """JzCzhz to Jzazbz."""

    jz, cz, hz = jzczhz
    hz = util.no_nan(hz)

    # If, for whatever reason (mainly direct user input),
    # if chroma is less than zero, clamp to zero.
    if cz < 0.0:
        cz = 0.0

    return (
        jz,
        cz * math.cos(math.radians(hz)),
        cz * math.sin(math.radians(hz))
    )


class JzCzhz(Cylindrical, Space):
    """
    JzCzhz class.

    https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
    """

    SPACE = "jzczhz"
    CHANNEL_NAMES = ("jz", "chroma", "hue", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = _cat.WHITES["D65"]

    RANGE = (
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([Angle(0.0), Angle(360.0)]),
    )

    @property
    def jz(self):
        """Jz."""

        return self._coords[0]

    @jz.setter
    def jz(self, value):
        """Set jz."""

        self._coords[0] = self._handle_input(value)

    @property
    def chroma(self):
        """Chroma."""

        return self._coords[1]

    @chroma.setter
    def chroma(self, value):
        """Set chroma."""

        self._coords[1] = self._handle_input(value)

    @property
    def hue(self):
        """Hue."""

        return self._coords[2]

    @hue.setter
    def hue(self, value):
        """Set hue."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def null_adjust(cls, coords, alpha):
        """On color update."""

        if coords[1] < ACHROMATIC_THRESHOLD:
            coords[2] = util.NaN
        return coords, alpha

    @classmethod
    def _to_jzazbz(cls, jzczhz):
        """To Jzazbz."""

        return jzczhz_to_jzazbz(jzczhz)

    @classmethod
    def _from_jzazbz(cls, jzazbz):
        """From Jzazbz."""

        return jzazbz_to_jzczhz(jzazbz)

    @classmethod
    def _to_xyz(cls, jzczhz):
        """To XYZ."""

        return Jzazbz._to_xyz(cls._to_jzazbz(jzczhz))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return cls._from_jzazbz(Jzazbz._from_xyz(xyz))
