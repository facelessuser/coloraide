"""
JzCzhz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from __future__ import annotations
from ..cat import WHITES
from .lch import LCh
from .jzazbz import Jzazbz
from ..channels import Channel, FLG_ANGLE
from ..types import Vector


class JzCzhz(LCh):
    """
    JzCzhz class.

    https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
    """

    BASE = "jzazbz"
    NAME = "jzczhz"
    SERIALIZE = ("--jzczhz",)
    WHITE = WHITES['2deg']['D65']
    DYNAMIC_RANGE = 'hdr'
    CHANNEL_ALIASES = {
        "lightness": "jz",
        "chroma": "cz",
        "hue": "hz"
    }
    ACHROMATIC = Jzazbz.ACHROMATIC
    CHANNELS = (
        Channel("jz", 0.0, 1.0, limit=(0.0, None)),
        Channel("cz", 0.0, 0.5, limit=(0.0, None)),
        Channel("hz", 0.0, 360.0, flags=FLG_ANGLE, nans=ACHROMATIC.hue)
    )

    def is_achromatic(self, undefined: list[bool], coords: Vector) -> bool | None:
        """Check if color is achromatic."""

        ldef, cdef, hdef = undefined
        if ldef and cdef:
            return False

        elif cdef:
            return coords[0] == 0.0

        elif ldef:
            return coords[1] < 1e-4

        return (
            coords[0] == 0.0 or
            self.ACHROMATIC.test(coords[0], coords[1], self.ACHROMATIC.hue if hdef else coords[2])
        )

    def achromatic_hue(self) -> float:
        """Ideal hue for conversion."""

        return self.ACHROMATIC.hue

    def hue_name(self) -> str:
        """Hue name."""

        return "hz"
