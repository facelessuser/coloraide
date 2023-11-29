"""
CAM 16 UCS.

https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067
https://doi.org/10.1002/col.22131
"""
from __future__ import annotations
import math
from .cam16_jmh import CAM16JMh
from ..spaces import Space, Labish
from ..cat import WHITES
from .. import util
from ..channels import Channel, FLG_MIRROR_PERCENT
from ..types import Vector

COEFFICENTS = {
    'lcd': (0.77, 0.007, 0.0053),
    'scd': (1.24, 0.007, 0.0363),
    'ucs': (1.00, 0.007, 0.0228)
}


def cam16_jmh_to_cam16_ucs(jmh: Vector, model: str) -> Vector:
    """
    CAM16 (Jab) to CAM16 UCS (Jab).

    We can actually go between simply by removing the old colorfulness multiplier
    and then adding the new adjusted multiplier. Then we can just adjust lightness.
    """

    J, M, h = jmh

    c1, c2 = COEFFICENTS[model][1:]

    M = math.log(1 + c2 * M) / c2
    a = M * math.cos(math.radians(h))
    b = M * math.sin(math.radians(h))

    return [
        (1 + 100 * c1) * J / (1 + c1 * J),
        a,
        b
    ]


def cam16_ucs_to_cam16_jmh(ucs: Vector, model: str) -> Vector:
    """
    CAM16 UCS (Jab) to CAM16 (Jab).

    We can actually go between simply by removing the old colorfulness multiplier
    and then adding the new adjusted multiplier. Then we can just adjust lightness.
    """

    J, a, b = ucs

    c1, c2 = COEFFICENTS[model][1:]

    M = math.sqrt(a ** 2 + b ** 2)
    M = (math.exp(M * c2) - 1) / c2
    h = math.degrees(math.atan2(b, a))

    return [
        J / (1 - c1 * (J - 100)),
        M,
        util.constrain_hue(h)
    ]


class CAM16UCS(Labish, Space):
    """CAM16 UCS (Jab) class."""

    BASE = "cam16-jmh"
    NAME = "cam16-ucs"
    SERIALIZE = ("--cam16-ucs",)
    MODEL = 'ucs'
    CHANNELS = (
        Channel("j", 0.0, 100.0),
        Channel("a", -50.0, 50.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -50.0, 50.0, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "lightness": "j"
    }
    WHITE = WHITES['2deg']['D65']
    # Use the same environment as CAM16JMh
    ENV = CAM16JMh.ENV
    ACHROMATIC = CAM16JMh.ACHROMATIC

    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resolve channels."""

        if index in (1, 2):
            if not math.isnan(coords[index]):
                return coords[index]

            return self.ACHROMATIC.get_ideal_ab(coords[0])[index - 1]

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        j, m, h = cam16_ucs_to_cam16_jmh(coords, self.MODEL)
        return j <= 0.0 or self.ACHROMATIC.test(j, m, h)

    def to_base(self, coords: Vector) -> Vector:
        """To CAM16 JMh from CAM16."""

        return cam16_ucs_to_cam16_jmh(coords, self.MODEL)

    def from_base(self, coords: Vector) -> Vector:
        """From CAM16 JMh to CAM16."""

        return cam16_jmh_to_cam16_ucs(coords, self.MODEL)


class CAM16LCD(CAM16UCS):
    """CAM16 LCD (Jab) class."""

    NAME = "cam16-lcd"
    SERIALIZE = ("--cam16-lcd",)
    MODEL = 'lcd'
    CHANNELS = (
        Channel("j", 0.0, 100.0, limit=(0.0, None)),
        Channel("a", -70.0, 70.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -70.0, 70.0, flags=FLG_MIRROR_PERCENT)
    )


class CAM16SCD(CAM16UCS):
    """CAM16 SCD (Jab) class."""

    NAME = "cam16-scd"
    SERIALIZE = ("--cam16-scd",)
    MODEL = 'scd'
    CHANNELS = (
        Channel("j", 0.0, 100.0, limit=(0.0, None)),
        Channel("a", -40.0, 40.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -40.0, 40.0, flags=FLG_MIRROR_PERCENT)
    )
