"""
DIN99o class.

https://de.wikipedia.org/wiki/DIN99-Farbraum
"""
from __future__ import annotations
from ..cat import WHITES
from .lab import Lab
import math
from ..types import Vector
from ..channels import Channel, FLG_MIRROR_PERCENT

KE = 1
KCH = 1

# --- DIN99o ---
# C1 was a bit off due to rounding and gave us less than 100
# lightness when translating from sRGB white.
# Solving the equation for a lightness of 100 and `KE` of 1,
# which should give us a 100 lightness for white:
#
# ```
# L99o = (303.67 * ln(1 + 0.0039 * L*)) / KE
# 303.67 = 100 / ln(1 + 0.0039 * 100)
# 303.67 = 100 / ln(1.39)
# ```
#
# This gives 303.67100547050995 without rounding and fixes
# white translation.
RADS = math.radians(26)
FACTOR = 0.83
C1 = 100 / math.log(1.39)
C2 = 0.0039
C3 = 0.075
C4 = 0.0435


def lab_to_din99o(lab: Vector) -> Vector:
    """XYZ to DIN99o."""

    l, a, b = lab
    val = 1 + abs(C2 * l)
    l99o = C1 * math.copysign(1, l) * math.log(val) / KE

    if a == 0 and b == 0:
        a99o = b99o = 0.0
    else:
        eo = a * math.cos(RADS) + b * math.sin(RADS)
        fo = FACTOR * (b * math.cos(RADS) - a * math.sin(RADS))
        go = math.sqrt(eo ** 2 + fo ** 2)
        val = 1 + C3 * go
        c99o = math.log(val) / (C4 * KE * KCH)
        h99o = math.atan2(fo, eo) + RADS

        a99o = c99o * math.cos(h99o)
        b99o = c99o * math.sin(h99o)

    return [l99o, a99o, b99o]


def din99o_lab_to_lch(lab: Vector) -> Vector:
    """
    Convert DIN99o Lab to LCh.

    Hue is in radians.
    """

    l99o, a99o, b99o = lab
    h99o = math.atan2(b99o, a99o)
    c99o = math.sqrt(a99o ** 2 + b99o ** 2)

    return [l99o, c99o, h99o]


def din99o_to_lab(din99o: Vector) -> Vector:
    """DIN99o to XYZ."""

    l99o, c99o, h99o = din99o_lab_to_lch(din99o)
    val = C4 * c99o * KCH * KE
    g = (math.exp(val) - 1) / C3
    e = g * math.cos(h99o - RADS)
    f = g * math.sin(h99o - RADS)

    return [
        math.copysign(1, l99o) * (math.exp((abs(l99o) * KE) / C1) - 1) / C2,
        e * math.cos(RADS) - (f / FACTOR) * math.sin(RADS),
        e * math.sin(RADS) + (f / FACTOR) * math.cos(RADS)
    ]


class DIN99o(Lab):
    """DIN99o class."""

    BASE = 'xyz-d65'
    NAME = "din99o"
    SERIALIZE = ("--din99o",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("a", -55.0, 55.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -55.0, 55.0, flags=FLG_MIRROR_PERCENT)
    )

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from DIN99o."""

        return super().to_base(din99o_to_lab(coords))

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to DIN99o."""

        return lab_to_din99o(super().from_base(coords))
