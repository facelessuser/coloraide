"""
JzCzhz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from ..spaces import Space, Lchish
from ..cat import WHITES
from ..gamut.bounds import GamutUnbound, FLG_ANGLE, FLG_OPT_PERCENT
from .. import util
import math
from .. import algebra as alg
from ..types import Vector
from typing import Tuple

ACHROMATIC_THRESHOLD = 0.0003


def jzazbz_to_jzczhz(jzazbz: Vector) -> Vector:
    """Jzazbz to JzCzhz."""

    jz, az, bz = jzazbz

    cz = math.sqrt(az ** 2 + bz ** 2)
    hz = math.degrees(math.atan2(bz, az))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if cz < ACHROMATIC_THRESHOLD:
        hz = alg.NaN

    return [jz, cz, util.constrain_hue(hz)]


def jzczhz_to_jzazbz(jzczhz: Vector) -> Vector:
    """JzCzhz to Jzazbz."""

    jz, cz, hz = jzczhz
    if alg.is_nan(hz):  # pragma: no cover
        return [jz, 0.0, 0.0]

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
    WHITE = WHITES['2deg']['D65']

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

        self._coords[0] = value

    @property
    def cz(self) -> float:
        """Chroma."""

        return self._coords[1]

    @cz.setter
    def cz(self, value: float) -> None:
        """Set chroma."""

        self._coords[1] = alg.clamp(value, 0.0)

    @property
    def hz(self) -> float:
        """Hue."""

        return self._coords[2]

    @hz.setter
    def hz(self, value: float) -> None:
        """Set hue."""

        self._coords[2] = value

    @classmethod
    def null_adjust(cls, coords: Vector, alpha: float) -> Tuple[Vector, float]:
        """On color update."""

        coords = alg.no_nans(coords)
        if coords[1] < ACHROMATIC_THRESHOLD:
            coords[2] = alg.NaN

        return coords, alg.no_nan(alpha)

    @classmethod
    def hue_name(cls) -> str:
        """Hue name."""

        return "hz"

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To Jzazbz from JzCzhz."""

        return jzczhz_to_jzazbz(coords)

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From Jzazbz to JzCzhz."""

        return jzazbz_to_jzczhz(coords)
