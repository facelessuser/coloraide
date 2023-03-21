"""
JzCzhz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from __future__ import annotations
from ..spaces import Space, LChish
from ..cat import WHITES
from .jzazbz import xyz_d65_to_jzazbz
from ..channels import Channel, FLG_ANGLE
from .. import util
import math
from ..types import Vector

# The transform consistently yields ~216 for achromatic hues for positive lightness
# Replacing achromatic NaN hues with this hue gives us closer translations back.
ACHROMATIC_HUE = 216.0777045520467
ACHROMATIC_THRESHOLD = 0.0003


def jzazbz_to_jzczhz(jzazbz: Vector) -> Vector:
    """Jzazbz to JzCzhz."""

    jz, az, bz = jzazbz

    cz = math.sqrt(az ** 2 + bz ** 2)
    hz = math.degrees(math.atan2(bz, az))

    return [jz, cz, util.constrain_hue(hz)]


def jzczhz_to_jzazbz(jzczhz: Vector) -> Vector:
    """JzCzhz to Jzazbz."""

    jz, cz, hz = jzczhz

    return [
        jz,
        cz * math.cos(math.radians(hz)),
        cz * math.sin(math.radians(hz))
    ]


class JzCzhz(LChish, Space):
    """
    JzCzhz class.

    https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
    """

    BASE = "jzazbz"
    NAME = "jzczhz"
    SERIALIZE = ("--jzczhz",)
    WHITE = WHITES['2deg']['D65']
    DYNAMIC_RANGE = 'hdr'
    ACHROMATIC_HUE = jzazbz_to_jzczhz(xyz_d65_to_jzazbz(util.xy_to_xyz(WHITE)))[-1]
    CHANNELS = (
        Channel("jz", 0.0, 1.0, limit=(0.0, None)),
        Channel("cz", 0.0, 0.5, limit=(0.0, None)),
        Channel("hz", 0.0, 360.0, flags=FLG_ANGLE, nans=ACHROMATIC_HUE)
    )
    CHANNEL_ALIASES = {
        "lightness": "jz",
        "chroma": "cz",
        "hue": "hz"
    }

    def is_achromatic(self, undefined: list[bool], coords: Vector) -> bool | None:
        """Check if color is achromatic."""

        ldef, cdef, _ = undefined
        if ldef and cdef:
            return False

        elif cdef:
            return coords[0] == 0.0

        elif ldef:
            return coords[1] < ACHROMATIC_THRESHOLD

        return coords[0] == 0.0 or coords[1] < ACHROMATIC_THRESHOLD

    def achromatic_hue(self) -> float:
        """Ideal hue for conversion."""

        return self.ACHROMATIC_HUE

    def hue_name(self) -> str:
        """Hue name."""

        return "hz"

    def to_base(self, coords: Vector) -> Vector:
        """To Jzazbz from JzCzhz."""

        return jzczhz_to_jzazbz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From Jzazbz to JzCzhz."""

        return jzazbz_to_jzczhz(coords)
