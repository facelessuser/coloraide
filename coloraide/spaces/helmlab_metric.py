"""
Helmlab MetricSpace - 13-stage perceptual color space.

MetricSpace~v21.

A data-driven analytical color space trained on 64,000+ individual human
color perception observations. Achieves 20.1% lower STRESS than CIEDE2000
on the COMBVD dataset (3,813 color pairs).

Pipeline: XYZ -> M1 -> γ -> M2 -> hue correction -> H-K -> cubic L -> dark L
   -> hue-dependent chroma scale -> chroma power -> L-dependent chroma scale
   -> HLC interaction -> hue-dependent lightness -> neutral correction -> rotation

- https://arxiv.org/abs/2602.23010
- https://github.com/Grkmyldz148/helmlab
"""
from __future__ import annotations
from .lab import Lab
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT
from .. import algebra as alg
from ..types import Vector
import math

M1 = [
    [0.72129864331134985189, 0.45344826541531813024, -0.19288975751942616377],
    [-0.78821186949557897616, 1.79524137675723594043, 0.08761724511817850503],
    [-0.09177005999121559676, 0.45765588659459255361, 1.29220455139176770842]
]

M1_INV = [
    [1.065107295808859, -0.3150044075301122, 0.1803492381741039],
    [0.4721107713837796, 0.4271995765962455, 0.04150680489380985],
    [-0.09156391926309541, -0.1736709363194979, 0.7719790382558294]
]

M2 = [
    [-0.26355622180094095963, 0.41683228837031738312, 0.49267631416564028335],
    [1.88975705087773215851, -3.12122320342057735232, 1.04216669210603840590],
    [0.35851086179620561545, 1.76940281937903676202, -1.41206260676953720967]
]

M2_INV = [
    [0.9183897822815019, 0.5232051237088666, 0.7065804598090856],
    [1.0899090574433024, 0.07005324849041904, 0.4319776874787044],
    [1.598895729264209, 0.22061850068770233, 0.012506037355220951]
]

GAMMA = [0.47229813098762524, 0.5149184096354483, 0.5113233386366979]

# Enrichment parameters
HUE_COS1 = -0.02833024015436984
HUE_COS2 = 0.2189784817615645
HUE_COS3 = 0.005506053349515315
HUE_COS4 = -0.053592461436994296

HUE_SIN1 = -0.21131429516166544
HUE_SIN2 = -0.06871898981942523
HUE_SIN3 = -0.0641329861299175
HUE_SIN4 = -0.00954137464208059

HK_WEIGHT = 0.2676231133101982
HK_POWER = 0.8934892185255707
HK_HUE_MOD = 0.7173169828841472
HK_SIN1 = 0.6915224124600773
HK_COS2 = 0.48647127559605596
HK_SIN2 = 0.9853124591201782

L_CORR_P1 = 0.5385456675962418
L_CORR_P2 = 0.12508858146241716
L_CORR_P3 = 0.6768950256217603
LH_COS1 = -0.4963251525324449
LH_SIN1 = -0.09564696283240552

LP_DARK = -0.029053748937210654
LP_DARK_HCOS = 1.3346761652952872
LLP_DARK_HSIN = -0.1698908144723919

CS_COS1 = -0.195370576218515
CS_COS2 = 0.08863325582067766
CS_COS3 = 0.13789738139719568
CS_COS4 = 0.0641970862504494

CS_SIN1 = 0.5330819227283227
CS_SIN2 = 0.9365540137751136
CS_SIN3 = 0.061650260197979936
CS_SIN4 = -0.027401052793571013

CP_COS1 = -0.09900209889026965
CP_COS2 = -0.013586499967803128

CP_SIN1 = 0.059635520647228726
CP_SIN2 = 0.2253393118474472

LC1 = -1.5239477450767043
LC2 = -1.751157310240011

HLC_COS1 = -0.43576378069144767
HLC_COS2 = 0.47931193034584496

HLC_SIN1 = 1.060094063845983
HLC_SIN2 = -0.2622579649434462

HL_COS1 = 0.13610794232685908
HL_COS2 = -0.01617739641422492

HL_SIN1 = 0.1168702235362288
HL_SIN2 = 0.038145638815030566

# Rigid rotation `φ = -28.2°`
PHI = -28.2 * math.pi / 180
ROT_COS = math.cos(PHI)
ROT_SIN = math.sin(PHI)


def xyz_d65_to_helmlab(xyz: Vector) -> Vector:
    """Convert XYZ to Helmlab."""

    lms = alg.matmul_x3(M1, xyz, dims=alg.D2_D1)
    cx = [alg.spow(a, b) for a, b in zip(lms, GAMMA)]
    return alg.matmul_x3(M2, cx, dims=alg.D2_D1)


def helmlab_to_xyz(lab: Vector) -> Vector:
    """Convert Helmlab to XYZ."""

    cx = alg.matmul_x3(M2_INV, lab, dims=alg.D2_D1)
    lms = [alg.spow(a, 1 / b) for a, b in zip(cx, GAMMA)]
    return alg.matmul_x3(M1_INV, lms, dims=alg.D2_D1)


def hue_delta(h: float) -> float:
    """Calculate `δ(h)` = Fourier series for hue rotation (up to 4th harmonic)."""
    return (
        HUE_COS1 * math.cos(h) + HUE_SIN1 * math.sin(h) +
        HUE_COS2 * math.cos(2 * h) + HUE_SIN2 * math.sin(2 * h) +
        HUE_COS3 * math.cos(3 * h) + HUE_SIN3 * math.sin(3 * h) +
        HUE_COS4 * math.cos(4 * h) + HUE_SIN4 * math.sin(4 * h)
    )


def hue_delta_deriv(h: float) -> float:
    """Calculate `d/dh` of `δ(h)`, needed for Newton iteration in inverse."""

    return (
        -HUE_COS1 * math.sin(h) + HUE_SIN1 * math.cos(h) +
        -2 * HUE_COS2 * math.sin(2 * h) + 2 * HUE_SIN2 * math.cos(2 * h) +
        -3 * HUE_COS3 * math.sin(3 * h) + 3 * HUE_SIN3 * math.cos(3 * h) +
        -4 * HUE_COS4 * math.sin(4 * h) + 4 * HUE_SIN4 * math.cos(4 * h)
    )


def chroma_scale_h (h: float) -> float:
    """Calculate `S(h) = exp(Fourier series up to 4th harmonic)`. Always > 0."""

    return math.exp(
        CS_COS1 * math.cos(h) + CS_SIN1 * math.sin(h) +
        CS_COS2 * math.cos(2 * h) + CS_SIN2 * math.sin(2 * h) +
        CS_COS3 * math.cos(3 * h) + CS_SIN3 * math.sin(3 * h) +
        CS_COS4 * math.cos(4 * h) + CS_SIN4 * math.sin(4 * h)
    )


def l_chroma_scale(l: float) -> float:
    """Calculate `T(L) = exp(polynomial)`. Always > 0. Clips exponent for extreme L."""

    dL = l - 0.5
    return math.exp(alg.clamp(LC1 * dL + LC2 * dL * dL, -30, 30))


def hlc_scale(h: float, l: float) -> float:
    """Hue x Lightness chroma interaction: `exp((L-0.5) * Fourier(h))`. Always > 0."""

    hueFactor = (
        HLC_COS1 * math.cos(h) + HLC_SIN1 * math.sin(h) +
        HLC_COS2 * math.cos(2 * h) + HLC_SIN2 * math.sin(2 * h)
    )
    return math.exp(alg.clamp((l - 0.5) * hueFactor, -30, 30))


def hue_lightness_scale(h: float) -> float:
    """Calculate `exp(Fourier(h))` - pure hue -> lightness modulation. Always > 0."""

    return math.exp(
        HL_COS1 * math.cos(h) + HL_SIN1 * math.sin(h) +
        HL_COS2 * math.cos(2 * h) + HL_SIN2 * math.sin(2 * h)
    )


def chroma_power_h(h: float) -> float:
    """Calculate `1 + Fourier(h, 2 harmonics)` - exponent for chroma power compression."""

    return (
        1 + CP_COS1 * math.cos(h) + CP_SIN1 * math.sin(h) +
        CP_COS2 * math.cos(2 * h) + CP_SIN2 * math.sin(2 * h)
    )


def l_correct_fwd (l: float, h: float) -> float:
    """Calculate `L1 = L_raw + p1*t + p2*t*(0.5-L) + p3*t^2 [+ t*Lh(h)], t = L*(1-L)`."""

    t = l * (1 - l)
    result = l + L_CORR_P1 * t + L_CORR_P2 * t * (0.5 - l) + L_CORR_P3 * t * t
    result += t * (LH_COS1 * math.cos(h) + LH_SIN1 * math.sin(h))
    return result


def l_correct_inv (l1: float, h: float) -> float:
    """Invert L correction via Newton iteration."""

    lh = LH_COS1 * math.cos(h) + LH_SIN1 * math.sin(h)
    l = l1
    for _ in range(15):
        t = l * (1 - l)
        dt = 1 - 2 * l
        f = (
            l + (L_CORR_P1 + lh) * t + L_CORR_P2 * t * (0.5 - l) +
            L_CORR_P3 * t * t - l1
        )
        dfdL = (
            1 + (L_CORR_P1 + lh) * dt +
            L_CORR_P2 * (dt * (0.5 - l) - t) +
            L_CORR_P3 * 2 * t * dt
        )
        if abs(dfdL) < 1e-10:  # pragma: no cover
            dfdL = 1

        l -= f / dfdL
    return l


def dark_l_fwd (l: float, h: float) -> float:
    """
    Calculate `L_new = L * exp(g), g = L*(1-L) ** 2 * coeff(h, S)`. Targets dark region.

    v13: coefficient is hue-dependent when `lp_dark_hcos/hsin != 0`.
    v16: coefficient is surround-dependent when `lp_dark_S/S2 != 0`.
    """

    coeff = LP_DARK + LP_DARK_HCOS * math.cos(h) + LLP_DARK_HSIN * math.sin(h)
    oml = (1.0 - l) if l < 1 else 0.0  # clamp at `L=1`: identity for `L>1`
    g = coeff * l * oml * oml
    return l * math.exp(alg.clamp(g, -30, 30))


def dark_l_inv (ln: float, h: float) -> float:
    """
    Invert dark L compression via Newton iteration.

    v13: coefficient is hue-dependent when `lp_dark_hcos/hsin != 0`.
    v16: coefficient is surround-dependent when `lp_dark_S/S2 != 0`.
    """

    coeff = LP_DARK + LP_DARK_HCOS * math.cos(h) + LLP_DARK_HSIN * math.sin(h)
    l = ln
    for _ in range(12):
        oml = (1.0 - l) if l < 1 else 0.0
        g = coeff * l * oml * oml
        eg = math.exp(alg.clamp(g, -30, 30))
        f = l * eg - ln
        gp = coeff * oml * (1 - 3 * l)
        fp = eg * (1 + l * gp)
        if abs(fp) < 1e-10:  # pragma: no cover
            fp = 1
        l -= f / fp
    return l


def xyz_d65_to_helmlab_full(xyz: Vector) -> Vector:
    """Convert XYZ to Helmlab."""

    l, a, b = xyz_d65_to_helmlab(xyz)

    # Stage 3.5: Hue correction (4-harmonic Fourier)
    h = math.atan2(b, a)
    c = math.sqrt(a * a + b * b)
    delta = hue_delta(h)
    h_new = h + delta
    a = c * math.cos(h_new)
    b = c * math.sin(h_new)


    # Stage 3.7: Helmholtz-Kohlrausch correction
    cr = math.sqrt(a * a + b * b)
    hkBoost = HK_WEIGHT * alg.spow(cr, alg.clamp(HK_POWER, 0.01, 10))
    hr = math.atan2(b, a)
    factor = (
        1 + HK_HUE_MOD * math.cos(hr) + HK_SIN1 * math.sin(hr) +
        HK_COS2 * math.cos(2 * hr) + HK_SIN2 * math.sin(2 * hr)
    )
    l += hkBoost * factor

    # Stage 4: Cubic L correction (with hue modulation)
    h = math.atan2(b, a)
    l = l_correct_fwd(l, h)

    # Stage 4.5: Dark L compression
    h = math.atan2(b, a)
    l = dark_l_fwd(l, h)

    # Stage 5: Hue-dependent chroma scaling
    h = math.atan2(b, a)
    cs = chroma_scale_h(h)
    a *= cs
    b *= cs

    # Stage 5.5: Nonlinear chroma power
    h = math.atan2(b, a)
    c = math.sqrt(a * a + b * b)
    p = chroma_power_h(h)
    cn = c ** p if c > 0 else 0
    a = cn * math.cos(h)
    b = cn * math.sin(h)

    # Stage 6: L-dependent chroma scaling
    t = l_chroma_scale(l)
    a *= t
    b *= t

    # Stage 6.5: HLC interaction
    h = math.atan2(b, a)
    hlcs = hlc_scale(h, l)
    a *= hlcs
    b *= hlcs

    # Stage 8: Hue-dependent lightness scaling
    h = math.atan2(b, a)
    l *= hue_lightness_scale(h)

    # Stage 11: Rigid rotation `(φ = -28.2°)`
    a_rot = a * ROT_COS - b * ROT_SIN
    b_rot = a * ROT_SIN + b * ROT_COS

    return [l, a_rot, b_rot]


def helmlab_full_to_xyz(lab: Vector) -> Vector:
    """Convert XYZ to Helmlab."""

    l, a, b = lab

    # Undo Stage 11: rotation
    aun = a * ROT_COS + b * ROT_SIN
    bun = -a * ROT_SIN + b * ROT_COS
    a = aun
    b = bun

    # Undo Stage 8: hue-dependent lightness
    h = math.atan2(b, a)
    l /= hue_lightness_scale(h)

    # Undo Stage 6.5: HLC
    h = math.atan2(b, a)
    hlcs = hlc_scale(h, l)
    a /= hlcs
    b /= hlcs

    # Undo Stage 6: L-dependent chroma
    t = l_chroma_scale(l)
    a /= t
    b /= t

    # Undo Stage 5.5: chroma power
    h = math.atan2(b, a)
    c = math.sqrt(a * a + b * b)
    p = chroma_power_h(h)
    co = c ** (1 / p) if c > 0 else 0
    a = co * math.cos(h)
    b = co * math.sin(h)

    # Undo Stage 5: chroma scaling
    h = math.atan2(b, a)
    cs = chroma_scale_h(h)
    a /= cs
    b /= cs

    # Undo Stage 4.5: dark L
    h = math.atan2(b, a)
    l = dark_l_inv(l, h)

    # Undo Stage 4: cubic L
    h = math.atan2(b, a)
    l = l_correct_inv(l, h)

    # Undo Stage 3.7: H-K
    cr = math.sqrt(a * a + b * b)
    hkBoost = HK_WEIGHT * pow(cr, alg.clamp(HK_POWER, 0.01, 10))
    hr = math.atan2(b, a)
    factor = (
        1 + HK_HUE_MOD * math.cos(hr) + HK_SIN1 * math.sin(hr) +
        HK_COS2 * math.cos(2 * hr) + HK_SIN2 * math.sin(2 * hr)
    )
    l -= hkBoost * factor

    # Undo Stage 3.5: hue correction (Newton iteration)
    h_out = math.atan2(b, a)
    c = math.sqrt(a * a + b * b)
    h_raw = h_out
    for _ in range(8):
        f = h_raw + hue_delta(h_raw) - h_out
        fp = 1 + hue_delta_deriv(h_raw)
        if abs(fp) < 1e-10:  # pragma: no cover
            fp = 1
        h_raw -= f / fp
    a = c * math.cos(h_raw)
    b = c * math.sin(h_raw)

    return helmlab_to_xyz([l, a, b])


class HelmlabMetric(Lab):
    """Helmlab class."""

    BASE = "xyz-d65"
    NAME = "helmlab-metric"
    SERIALIZE = ("--helmlab-metric",)
    CHANNELS = (
        Channel("l", 0.0, 1.6),
        Channel("a", -1.5, 1.5, flags=FLG_MIRROR_PERCENT),
        Channel("b", -1.5, 1.5, flags=FLG_MIRROR_PERCENT)
    )
    WHITE = WHITES['2deg']['ASTM-E308-D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return helmlab_full_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_d65_to_helmlab_full(coords)
