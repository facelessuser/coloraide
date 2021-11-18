"""
JzCzhz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, Lchish, FLG_ANGLE, FLG_OPT_PERCENT
from .. import util
import re
import math
from ..util import MutableVector
from typing import Tuple

ACHROMATIC_THRESHOLD = 0.0003


def jzazbz_to_jzczhz(jzazbz: MutableVector) -> MutableVector:
    """Jzazbz to JzCzhz."""

    jz, az, bz = jzazbz

    cz = math.sqrt(az ** 2 + bz ** 2)
    hz = math.degrees(math.atan2(bz, az))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if cz < ACHROMATIC_THRESHOLD:
        hz = util.NaN

    return [jz, cz, util.constrain_hue(hz)]


def jzczhz_to_jzazbz(jzczhz: MutableVector) -> MutableVector:
    """JzCzhz to Jzazbz."""

    jz, cz, hz = jzczhz
    hz = util.no_nan(hz)

    # If, for whatever reason (mainly direct user input),
    # if chroma is less than zero, clamp to zero.
    if cz < 0.0:
        cz = 0.0

    return [
        jz,
        cz * math.cos(math.radians(hz)),
        cz * math.sin(math.radians(hz))
    ]


class JzCzhz(Lchish, Space):
    """
    JzCzhz class.

    https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
    """

    BASE = "jzazbz"
    NAME = "jzczhz"
    SERIALIZE = ("--jzczhz",)
    CHANNEL_NAMES = ("jz", "cz", "hz")
    CHANNEL_ALIASES = {
        "lightness": "jz",
        "chroma": "cz",
        "hue": "hz"
    }
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    BOUNDS = (
        GamutUnbound(0.0, 1.0, FLG_OPT_PERCENT),
        GamutUnbound(0.0, 1.0),
        GamutUnbound(0.0, 360.0, FLG_ANGLE)
    )

    @property
    def jz(self) -> float:
        """Jz."""

        return self._coords[0]

    @jz.setter
    def jz(self, value: float) -> None:
        """Set jz."""

        self._coords[0] = self._handle_input(value)

    @property
    def cz(self) -> float:
        """Chroma."""

        return self._coords[1]

    @cz.setter
    def cz(self, value: float) -> None:
        """Set chroma."""

        self._coords[1] = self._handle_input(value)

    @property
    def hz(self) -> float:
        """Hue."""

        return self._coords[2]

    @hz.setter
    def hz(self, value: float) -> None:
        """Set hue."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def null_adjust(cls, coords: MutableVector, alpha: float) -> Tuple[MutableVector, float]:
        """On color update."""

        if coords[1] < ACHROMATIC_THRESHOLD:
            coords[2] = util.NaN

        return coords, alpha

    @classmethod
    def hue_name(cls) -> str:
        """Hue name."""

        return "hz"

    @classmethod
    def to_base(cls, coords: MutableVector) -> MutableVector:
        """To Jzazbz from JzCzhz."""

        return jzczhz_to_jzazbz(coords)

    @classmethod
    def from_base(cls, coords: MutableVector) -> MutableVector:
        """From Jzazbz to JzCzhz."""

        return jzazbz_to_jzczhz(coords)
