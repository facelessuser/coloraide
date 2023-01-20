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

A = 0.17883277
B = 0.28466892  # `1 - 4 * A`
C = 0.55991073  # `0.5 - A * alg.nlog(4 * A)`
SCALE = 0.26496256042100724
INV_SCALE = 1 / SCALE


def hlg_oetf(values: Vector) -> Vector:
    """HLG OETF."""

    adjusted = []  # type: Vector
    for e in values:
        adjusted.append(alg.nth_root(3 * e, 2) if e <= 1 / 12 else A * alg.nlog(12 * e - B) + C)
    return adjusted


def hlg_eotf(values: Vector) -> Vector:
    """HLG EOTF."""

    adjusted = []  # type: Vector
    for e in values:
        adjusted.append((e ** 2) / 3 if e <= 0.5 else (alg.nexp((e - C) / A) + B) / 12)
    return adjusted


class Rec2100HLG(sRGB):
    """Rec. 2100 HLG class."""

    BASE = "rec2020-linear"
    NAME = "rec2100-hlg"
    SERIALIZE = ('--rec2100-hlg',)
    WHITE = WHITES['2deg']['D65']
    DYNAMIC_RANGE = 'hdr'

    def to_base(self, coords: Vector) -> Vector:
        """To base from Rec 2100 HLG."""

        return alg.multiply(hlg_eotf(coords), INV_SCALE, dims=alg.D1_SC)

    def from_base(self, coords: Vector) -> Vector:
        """From base to Rec. 2100 HLG."""

        return hlg_oetf(alg.multiply(coords, SCALE, dims=alg.D1_SC))
