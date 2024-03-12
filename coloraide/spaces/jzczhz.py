"""
JzCzhz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from __future__ import annotations
from ..cat import WHITES
from .lch import LCh
from .jzazbz import ACHROMATIC_THRESHOLD  # type: ignore[attr-defined]
from ..channels import Channel, FLG_ANGLE
from ..types import Vector


class JzCzhz(LCh):
    """
    JzCzhz class.

    https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
    """

    BASE = "jzazbz"
    NAME = "jzczhz"
    SERIALIZE = ("jzczhz", "--jzczhz",)
    WHITE = WHITES['2deg']['D65']
    DYNAMIC_RANGE = 'hdr'
    CHANNEL_ALIASES = {
        "lightness": "jz",
        "chroma": "cz",
        "hue": "hz",
        "h": 'hz',
        'c': 'cz',
        'j': 'jz'
    }
    CHANNELS = (
        Channel("jz", 0.0, 1.0),
        Channel("cz", 0.0, 1.0),
        Channel("hz", 0.0, 360.0, flags=FLG_ANGLE)
    )

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        # Account for both positive and negative chroma
        return coords[0] < 0 or abs(coords[1]) < ACHROMATIC_THRESHOLD

    def hue_name(self) -> str:
        """Hue name."""

        return "hz"
