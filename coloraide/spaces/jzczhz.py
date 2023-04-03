"""
JzCzhz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from __future__ import annotations
import math
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

    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resolve channels."""

        if index == 2:
            h = coords[2]
            return self.ACHROMATIC.get_ideal_hue(coords[0]) if math.isnan(h) else h

        elif index == 1:
            c = coords[1]
            return self.ACHROMATIC.get_ideal_chroma(coords[0]) if math.isnan(c) else c

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return coords[0] == 0.0 or self.ACHROMATIC.test(*coords)

    def hue_name(self) -> str:
        """Hue name."""

        return "hz"
