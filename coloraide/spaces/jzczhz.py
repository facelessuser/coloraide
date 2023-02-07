"""
JzCzhz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from __future__ import annotations
from ..spaces import Space, LChish
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .. import util
import math
from .. import algebra as alg
from ..types import Vector

ACHROMATIC_THRESHOLD = 0.0003
# The transform consistently yields ~216 for achromatic hues for positive lightness
# Replacing achromatic NaN hues with this hue gives us closer translations back.
ACHROMATIC_HUE = 216.0777045520467


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

    # For better round tripping of achromatic colors,
    # use the achromatic hue that occurs in forward transform.
    # We use the one from white translation. It may vary slightly
    # depending on the grayscale color, but only slightly,
    # so this is close enough.
    if cz < ACHROMATIC_THRESHOLD:
        hz = ACHROMATIC_HUE

    if alg.is_nan(hz):  # pragma: no cover
        return [jz, 0.0, 0.0]

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
    CHANNELS = (
        Channel("jz", 0.0, 1.0, limit=(0.0, None)),
        Channel("cz", 0.0, 0.5, limit=(0.0, None)),
        Channel("hz", 0.0, 360.0, flags=FLG_ANGLE)
    )
    CHANNEL_ALIASES = {
        "lightness": "jz",
        "chroma": "cz",
        "hue": "hz"
    }
    WHITE = WHITES['2deg']['D65']
    DYNAMIC_RANGE = 'hdr'

    def achromatic_hue(self) -> float:
        """Ideal achromatic hue."""

        return ACHROMATIC_HUE

    def normalize(self, coords: Vector) -> Vector:
        """On color update."""

        coords = alg.no_nans(coords)
        if coords[1] < ACHROMATIC_THRESHOLD:
            coords[2] = alg.NaN

        return coords

    def hue_name(self) -> str:
        """Hue name."""

        return "hz"

    def to_base(self, coords: Vector) -> Vector:
        """To Jzazbz from JzCzhz."""

        return jzczhz_to_jzazbz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From Jzazbz to JzCzhz."""

        return jzazbz_to_jzczhz(coords)
