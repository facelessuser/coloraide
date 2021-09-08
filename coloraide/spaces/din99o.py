"""
Din99o class.

https://de.wikipedia.org/wiki/DIN99-Farbraum
"""
from ..spaces import RE_DEFAULT_MATCH
from .xyz import XYZ
from .lab.base import LabBase, lab_to_xyz, xyz_to_lab
import re
import math

KE = 1
KCH = 1

# --- Din99o ---
RADS = math.radians(26)
FACTOR = 0.83
C1 = 303.67
C2 = 0.0039
C3 = 0.075
C4 = 0.0435

# --- Din99 ---
# RADS = math.radians(16)
# FACTOR = 0.7
# C1 = 105.51
# C2 = 0.0158
# C3 = 0.045
# C4 = 0.045


def lab_to_din99o(lab):
    """XYZ to Din99o."""

    l, a, b = lab
    l99o = C1 * math.log(1 + C2 * l) / KE

    if a == 0 and b == 0:
        a99o = b99o = 0
    else:
        eo = a * math.cos(RADS) + b * math.sin(RADS)
        fo = FACTOR * (b * math.cos(RADS) - a * math.sin(RADS))
        go = math.sqrt(eo ** 2 + fo ** 2)
        c99o = math.log(1 + C3 * go) / (C4 * KE * KCH)
        h99o = math.atan2(fo, eo) + RADS

        a99o = c99o * math.cos(h99o)
        b99o = c99o * math.sin(h99o)

    return [l99o, a99o, b99o]


def din99o_lab_to_lch(lab):
    """
    Convert Din99o Lab to Lch.

    Hue is in radians.
    """

    l99o, a99o, b99o = lab
    h99o = math.atan2(b99o, a99o)
    c99o = math.sqrt(a99o ** 2 + b99o ** 2)

    return [l99o, c99o, h99o]


def din99o_to_lab(din99o):
    """Din99o to XYZ."""

    l99o, c99o, h99o = din99o_lab_to_lch(din99o)
    g = (math.exp(C4 * c99o * KCH * KE) - 1) / C3
    e = g * math.cos(h99o - RADS)
    f = g * math.sin(h99o - RADS)

    return [
        (math.exp((l99o * KE) / C1) - 1) / C2,
        e * math.cos(RADS) - (f / FACTOR) * math.sin(RADS),
        e * math.sin(RADS) + (f / FACTOR) * math.cos(RADS)
    ]


class Din99o(LabBase):
    """Din99o class."""

    SPACE = "din99o-lab"
    SERIALIZE = ("--din99o-lab",)
    CHANNEL_NAMES = ("lightness", "a", "b", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    @classmethod
    def _to_xyz(cls, parent, lab):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lab_to_xyz(din99o_to_lab(lab), cls.white()))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return lab_to_din99o(xyz_to_lab(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz), cls.white()))
