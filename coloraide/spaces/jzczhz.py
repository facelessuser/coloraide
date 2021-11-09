"""
JzCzhz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, Lchish, FLG_ANGLE, FLG_OPT_PERCENT
from .jzazbz import Jzazbz
from .. import util
import re
import math
from ..util import Vector, MutableVector
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

ACHROMATIC_THRESHOLD = 0.0003


def jzazbz_to_jzczhz(jzazbz: Vector) -> MutableVector:
    """Jzazbz to JzCzhz."""

    jz, az, bz = jzazbz

    cz = math.sqrt(az ** 2 + bz ** 2)
    hz = math.degrees(math.atan2(bz, az))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if cz < ACHROMATIC_THRESHOLD:
        hz = util.NaN

    return [jz, cz, util.constrain_hue(hz)]


def jzczhz_to_jzazbz(jzczhz: Vector) -> MutableVector:
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

    SPACE = "jzczhz"
    SERIALIZE = ("--jzczhz",)
    CHANNEL_NAMES = ("jz", "cz", "hz", "alpha")
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
    def _to_jzazbz(cls, parent: 'Color', jzczhz: Vector) -> MutableVector:
        """To Jzazbz."""

        return jzczhz_to_jzazbz(jzczhz)

    @classmethod
    def _from_jzazbz(cls, parent: 'Color', jzazbz: Vector) -> MutableVector:
        """From Jzazbz."""

        return jzazbz_to_jzczhz(jzazbz)

    @classmethod
    def _to_xyz(cls, parent: 'Color', jzczhz: Vector) -> MutableVector:
        """To XYZ."""

        return Jzazbz._to_xyz(parent, cls._to_jzazbz(parent, jzczhz))

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """From XYZ."""

        return cls._from_jzazbz(parent, Jzazbz._from_xyz(parent, xyz))
