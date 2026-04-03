"""
Helmlab GenSpace: generation-optimized color space for interpolation.

A simplified pipeline (`XYZ -> M1 -> cbrt -> M2 -> NC`) optimized for
perceptually uniform gradients, palette generation, and color-mix.
Achieves 6x better hue accuracy than Oklab with 10% better perceptual
distance prediction.

Key differences from Helmlab (MetricSpace):
  - Shared gamma = 1/3 (cube root, guarantees achromatic a=b=0)
  - No enrichment stages (simpler, faster, better for generation)
  - Different M1/M2 matrices (Phase1H-optimized)

- https://arxiv.org/abs/2602.23010
- https://github.com/Grkmyldz148/helmlab
"""
from __future__ import annotations
import math
from .lab import Lab
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT
from .. import algebra as alg
from ..types import Vector

# Depressed cubic parameter
ALPHA = 0.021
S = math.sqrt(ALPHA / 3)
S3 = S ** 3

# Chroma power
CP = 0.978

# L-gated hue enrichment parameters
ENR_AMP = 0.058
ENR_CENTER = 264.5 * math.pi / 180 # radians
ENR_SIGMA = 0.7
ENR_LLO = 0.37
ENR_LHI = 1.0


M1 = [
    [0.8154374735648701, 0.3603221491264266, -0.12432703417946676],
    [0.03298391207546648, 0.9292940788255503, 0.03614494665290377],
    [0.048184113668356454, 0.26427748135788043, 0.6336388271114471]
]

M1_INV = [
    [1.2326502723725545, -0.555741473217925, 0.2735612008453706],
    [-0.04076658787624679, 1.1122097325799585, -0.07144314470371178],
    [-0.07673215022426162, -0.4216188546558441, 1.5871810048801054]
]

M2 = [
    [0.21186668013760682, 0.7989440040850104, -0.004099375589489282],
    [2.4672018828033475, -2.9877348024830788, 0.520532919679731],
    [-0.11390787868068575, 1.3932982808117473, -1.279390402131062]
]

M2_INV = [
    [0.9933334327571627, 0.32599327253052285, 0.12945085631713896],
    [0.9933334327571626, -0.08708353111074632, -0.03861361743004954],
    [0.9933334327571621, -0.12386097008215027, -0.8351991365871065]
]

# Piecewise linear L correction (21 breakpoints, v0.11.1)
PW_L_IN = [
    0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
    0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0
]

PW_L_OUT = [
    0, 0.009494013522189627, 0.02564569838030986, 0.055259661658689105, 0.10574901531227408,
    0.16055853320726027, 0.21405964892993756, 0.26786230508811226, 0.3220435246104499, 0.3739052098520243,
    0.43020997780918835, 0.4835465162128873, 0.5399824670411353, 0.5956710081330342, 0.6542161666450478,
    0.7115380216519989, 0.7702762412711669, 0.8293313467712837, 0.889406386197059, 0.9462829573474728,
    1.0
]

PW_N = len(PW_L_IN)


# Depressed cubic: y ** 3 + αy = x
def depcubic_fwd(x: float) -> float:
    """Depressed cubic forward."""
    t = x / (2 * S3)
    y = 2 * S * math.sinh(math.asinh(t) / 3)
    # Halley refinement
    f = y ** 3 + ALPHA * y - x
    fp = 3 * y * y + ALPHA
    fpp = 6 * y
    denom = 2 * fp * fp - f * fpp
    if abs(denom) > 1e-30:
        y -= 2 * f * fp / denom
    return y


def depcubic_inv(y: float) -> float:
    """Depressed cubic inverse."""

    return y * y * y + ALPHA * y


# L - gated hue enrichment
def enrich_gate(l: float) -> float:
    """Enrichment gate."""
    t = max(0, min(1, (l - ENR_LLO) / (ENR_LHI - ENR_LLO)))
    return math.sin(math.pi * t) ** 2


def enrich_fwd(l: float, a: float, b: float) -> Vector:
    """Enrichment forward."""
    c = math.sqrt(a ** 2 + b ** 2)
    if (c < 1e-12):
        return [a, b]

    gate = enrich_gate(l)
    if (gate < 1e-12):
        return [a, b]

    h = math.atan2(b, a)
    dh = h - ENR_CENTER
    dh = dh - round(dh / (2 * math.pi)) * 2 * math.pi
    gauss = math.exp(-0.5 * (dh / ENR_SIGMA) ** 2)
    h_new = h + ENR_AMP * gate * gauss
    return [c * math.cos(h_new), c * math.sin(h_new)]


def enrich_inv (l: float, a: float, b: float) -> Vector:
    """Inverse enrichment."""
    c = math.sqrt(a ** 2 + b ** 2)
    if (c < 1e-12):
        return [a, b]

    gate = enrich_gate(l)
    if (gate < 1e-12):
        return [a, b]

    h_target = math.atan2(b, a)
    sig2 = ENR_SIGMA * ENR_SIGMA
    ag = ENR_AMP * gate
    h = h_target
    for _ in range(8):
        dh = h - ENR_CENTER
        dh = dh - round(dh / (2 * math.pi)) * 2 * math.pi
        gauss = math.exp(-0.5 * dh * dh / sig2)
        f = h + ag * gauss - h_target
        fp = 1 + ag * gauss * (-dh / sig2)
        fpp = ag * gauss * (-1 / sig2 + dh * dh / (sig2 * sig2))
        den = 2 * fp * fp - f * fpp
        if abs(den) > 1e-30:
            h -= 2 * f * fp / den

    return [c * math.cos(h), c * math.sin(h)]


# PW L correction
def pw_l_fwd(l: float) -> float:
    """PW L correction (forward)."""
    if (l <= 0 or l >= 1):
        return l

    lo, hi  = 0, PW_N - 1
    while (hi - lo) > 1:
        mid = (lo + hi) >> 1
        if (PW_L_IN[mid] <= l):
            lo = mid
        else:
            hi = mid

    t = (l - PW_L_IN[lo]) / (PW_L_IN[hi] - PW_L_IN[lo])
    return PW_L_OUT[lo] + t * (PW_L_OUT[hi] - PW_L_OUT[lo])


def pw_l_inv(l: float) -> float:
    """PW L correction (inverse)."""
    if l <= PW_L_OUT[0] or l >= PW_L_OUT[PW_N - 1]:
        return l

    lo, hi = 0, PW_N - 1
    while (hi - lo) > 1:
        mid = (lo + hi) >> 1
        if PW_L_OUT[mid] <= l:
            lo = mid
        else:
            hi = mid

    t = (l - PW_L_OUT[lo]) / (PW_L_OUT[hi] - PW_L_OUT[lo])
    return PW_L_IN[lo] + t * (PW_L_IN[hi] - PW_L_IN[lo])


def xyz_d65_to_helmgen(xyz: Vector) -> Vector:
    """Convert XYZ to Helmgen."""

    # Stage 1: XYZ -> LMS (M1)
    lms = alg.matmul_x3(M1, xyz, dims=alg.D2_D1)
    c = [depcubic_fwd(max(v, 0)) for v in lms]

    # Stage 2.5: Smooth neutral blend (C∞ correction for achromatic precision)
    mean = sum(c) / 3
    mx = max(c)
    mn = min(c)
    spread = (mx - mn) / max(abs(mean), 1e-30)
    w = math.exp(-((spread / 1e-5) ** 2))
    c = [v + w * (mean - v) for v in c]

    # Stage 3: LMS_c -> Lab (M2)
    l, a, b = alg.matmul_x3(M2, c, dims=alg.D2_D1)

    # Stage 3.5: Chroma power (`cp=0.978`)
    chroma = math.sqrt(a ** 2 + b ** 2)
    if chroma > 1e-12:
        c_new = math.pow(chroma, CP)
        s = c_new / chroma
        a *= s
        b *= s

    # Stage 4: Piecewise-linear L correction
    l = pw_l_fwd(l)

    # Stage 5: L-gated hue enrichment
    a, b = enrich_fwd(l, a, b)

    return [l, a, b]


def helmgen_to_xyz(lab: Vector) -> Vector:
    """Convert Helmgen to XYZ."""

    l, a, b = lab

    # Undo Stage 5: L-gated hue enrichment
    a, b = enrich_inv(l, a, b)

    # Undo Stage 4: PW L correction
    l = pw_l_inv(l)

    # Undo Stage 3.5: Chroma power inverse (`C^(1/cp)`)
    chroma = math.sqrt(a ** 2 + b ** 2)
    if chroma > 1e-12:
        c_orig = math.pow(chroma, 1 / CP)
        s = c_orig / chroma
        a *= s
        b *= s

    # Undo Stage 3: Lab -> LMS_c (`M2_INV`)
    c = alg.matmul_x3(M2_INV, [l, a, b], dims=alg.D2_D1)

    # Undo Stage 2.5: Smooth neutral blend
    mean = sum(c) / 3
    mx = max(c)
    mn = min(c)
    spread = (mx - mn) / max(abs(mean), 1e-30)
    w = math.exp(-((spread / 1e-5) ** 2))
    c = [v + w * (mean - v) for v in c]

    # Undo Stage 2: Inverse depressed cubic (x = y ** 3 + αy)
    lms = [depcubic_inv(v) for v in c]

    # Undo Stage 1: LMS -> XYZ (`M1_INV`)
    return alg.matmul_x3(M1_INV, lms, dims=alg.D2_D1)


class Helmgen(Lab):
    """Helmgen class."""

    BASE = "xyz-d65"
    NAME = "helmgen"
    SERIALIZE = ("--helmgen",)
    CHANNELS = (
        Channel("l", 0.0, 1.0),
        Channel("a", -0.4, 0.4, flags=FLG_MIRROR_PERCENT),
        Channel("b", -0.4, 0.4, flags=FLG_MIRROR_PERCENT)
    )
    WHITE = WHITES['2deg']['ASTM-E308-D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return helmgen_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_d65_to_helmgen(coords)
