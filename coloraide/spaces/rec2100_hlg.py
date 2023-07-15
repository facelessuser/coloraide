"""
Rec 2100 HLG color class.

https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.2100-2-201807-I!!PDF-E.pdf

https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BT.2390-10-2021-PDF-E.pdf (page 25)

> Report ITU-R BT.2408 indicates that, for HLG HDR, diffuse white should be set at a signal level of
> 75%. This can be configured by making the output from an 18% grey card correspond to a signal
> level of 38%, rather than the 42.5% stated above.

https://lists.w3.org/Archives/Public/public-colorweb/2021Sep/0008.html

Suggests the scale of 0.26496256042100724 to satisfy the above requirement.

"""
from __future__ import annotations
from ..cat import WHITES
from .srgb import sRGB
from .. import algebra as alg
from ..types import Vector
import math

# Sets 18% grey card to ~38% (37.7...) in order to set diffused white to 75%.
SCALE = 0.26496256042100724


class Environment:
    """Class to calculate and contain any required environmental data."""

    def __init__(
        self,
        lw: float,
        lb: float,
        scale: float
    ):
        """Initialize environmental data."""

        self.a = 0.17883277
        self.b = 0.28466892  # `1 - 4 * a`
        self.c = 0.55991073  # `0.5 - a * math.log(4 * a)`
        self.beta = hlg_black_level_lift(lw, lb)
        self.scale = scale
        self.inv_scale = 1 / scale


def hlg_gamma(lw: float = 1000.0) -> float:
    """
    Return the reference HLG system gamma.

    Ranges should be `lw >= 1000 cd / m^2`.
    """

    return 1.2 + 0.42 * math.log(lw / 1000.0)


def hlg_black_level_lift(lw: float = 0.0, lb: float = 1000.0) -> float:
    """
    Return beta (the black level lift) using the nominal peak level luminance and display luminance for black.

    Ranges should be `lw >= 1000 cd / m^2` and `lb <= 0.005 cd / m^2`.
    """

    return math.sqrt(3 * (lb / lw) ** (1 / hlg_gamma(lw)))


def hlg_oetf(values: Vector, env: Environment) -> Vector:
    """HLG OETF."""

    adjusted = []  # type: Vector
    for e in values:
        e = alg.nth_root(3 * e, 2) if e <= 1 / 12 else env.a * math.log(12 * e - env.b) + env.c
        adjusted.append((e - env.beta) / (1 - env.beta))
    return adjusted


def hlg_eotf(values: Vector, env: Environment) -> Vector:
    """HLG EOTF."""

    adjusted = []  # type: Vector
    for e in values:
        e = (1 - env.beta) * e + env.beta
        adjusted.append((e ** 2) / 3 if e <= 0.5 else (math.exp((e - env.c) / env.a) + env.b) / 12)
    return adjusted


class Rec2100HLG(sRGB):
    """Rec. 2100 HLG class."""

    BASE = "rec2020-linear"
    NAME = "rec2100-hlg"
    SERIALIZE = ('--rec2100-hlg',)
    WHITE = WHITES['2deg']['D65']
    DYNAMIC_RANGE = 'hdr'
    ENV = Environment(1000, 0, SCALE)

    def to_base(self, coords: Vector) -> Vector:
        """To base from Rec 2100 HLG."""

        return [c * self.ENV.inv_scale for c in hlg_eotf(coords, self.ENV)]

    def from_base(self, coords: Vector) -> Vector:
        """From base to Rec. 2100 HLG."""

        return hlg_oetf([c * self.ENV.scale for c in coords], self.ENV)
