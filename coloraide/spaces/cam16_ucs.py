"""
CAM 16 UCS.

https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067
https://doi.org/10.1002/col.22131
"""
from __future__ import annotations
import math
from .cam16_jmh import CAM16JMh, xyz_d65_to_cam16, cam16_to_xyz_d65, Environment
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


def cam16_jmh_to_cam16_ucs(jmh: Vector, model: str, env: Environment) -> Vector:
    """
    CAM16 (Jab) to CAM16 UCS (Jab).

    We can actually go between simply by removing the old colorfulness multiplier
    and then adding the new adjusted multiplier. Then we can just adjust lightness.
    """

    J, M, h = jmh

    if J == 0.0:
        return [0.0, 0.0, 0.0]

    # Account for negative colorfulness by reconverting
    if M < 0:
        cam16 = xyz_d65_to_cam16(cam16_to_xyz_d65(J=J, M=M, h=h, env=env), env=env)
        J, M, h = cam16[0], cam16[5], cam16[2]

    c1, c2 = COEFFICENTS[model][1:]

    # Only in extreme cases (outside the visible spectrum)
    # can the input value for log become negative.
    # Avoid domain error by forcing zero.
    M = math.log(max(1 + c2 * M, 1.0)) / c2
    a = M * math.cos(math.radians(h))
    b = M * math.sin(math.radians(h))

    absj = abs(J)
    return [
        math.copysign((1 + 100 * c1) * absj / (1 + c1 * absj), J),
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

    if J == 0.0:
        return [0.0, 0.0, 0.0]

    c1, c2 = COEFFICENTS[model][1:]

    M = math.sqrt(a ** 2 + b ** 2)
    M = (math.exp(M * c2) - 1) / c2
    h = math.degrees(math.atan2(b, a))

    absj = abs(J)
    return [
        math.copysign(absj / (1 - c1 * (absj - 100)), J),
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
    INV_ACHROMATIC = CAM16JMh.INV_ACHROMATIC

    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resolve channels."""

        if index in (1, 2):
            # Assume black if J is below zero
            J = coords[0]

            achromatic = self.INV_ACHROMATIC if J < 0 else self.ACHROMATIC

            if not math.isnan(coords[index]):
                return coords[index]

            return achromatic.get_ideal_ab(J)[index - 1]

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        j, m, h = cam16_ucs_to_cam16_jmh(coords, self.MODEL)

        if j == 0.0:
            return True

        if j < 0.0:
            return self.INV_ACHROMATIC.test(j, m, h)

        return self.ACHROMATIC.test(j, m, h)

    def to_base(self, coords: Vector) -> Vector:
        """To CAM16 JMh from CAM16."""

        return cam16_ucs_to_cam16_jmh(coords, self.MODEL)

    def from_base(self, coords: Vector) -> Vector:
        """From CAM16 JMh to CAM16."""

        return cam16_jmh_to_cam16_ucs(coords, self.MODEL, self.ENV)


class CAM16LCD(CAM16UCS):
    """CAM16 LCD (Jab) class."""

    NAME = "cam16-lcd"
    SERIALIZE = ("--cam16-lcd",)
    MODEL = 'lcd'
    CHANNELS = (
        Channel("j", 0.0, 100.0),
        Channel("a", -70.0, 70.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -70.0, 70.0, flags=FLG_MIRROR_PERCENT)
    )


class CAM16SCD(CAM16UCS):
    """CAM16 SCD (Jab) class."""

    NAME = "cam16-scd"
    SERIALIZE = ("--cam16-scd",)
    MODEL = 'scd'
    CHANNELS = (
        Channel("j", 0.0, 100.0),
        Channel("a", -40.0, 40.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -40.0, 40.0, flags=FLG_MIRROR_PERCENT)
    )
