"""
ZCAM.

```
- ZCAM: https://opg.optica.org/oe/fulltext.cfm?uri=oe-29-4-6036&id=447640.
- Supplemental ZCAM (inverse transform): https://opticapublishing.figshare.com/articles/journal_contribution/\
  Supplementary_document_for_ZCAM_a_psychophysical_model_for_colour_appearance_prediction_-_5022171_pdf/13640927.
- Two-stage chromatic adaptation by Qiyan Zhai and Ming R. Luo using CAM02: https://opg.optica.org/oe/\
  fulltext.cfm?uri=oe-26-6-7724&id=383537
```
"""
from __future__ import annotations
import math
import bisect
from .. import util
from .. import algebra as alg
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from ..types import Vector, VectorLike
from .lch import LCh
from .jzazbz import izazbz_to_xyz, xyz_to_izazbz
from .. import cat

DEF_ILLUMINANT_BI = util.xyz_to_absxyz(util.xy_to_xyz(cat.WHITES['2deg']['E']), yw=100.0)
CAT02 = cat.CAT02.MATRIX
CAT02_INV = [
    [1.0961238208355142, -0.27886900021828726, 0.18274517938277304],
    [0.45436904197535916, 0.4735331543074118, 0.07209780371722913],
    [-0.009627608738429355, -0.00569803121611342, 1.0153256399545427]
]

# ZCAM uses a slightly different matrix than Jzazbz
# It updates how `Iz` is calculated.
LMS_P_TO_IZAZBZ = [
    [0.0, 1.0, 0.0],
    [3.524, -4.066708, 0.542708],
    [0.199076, 1.096799, -1.295875]
]
IZAZBZ_TO_LMS_P = alg.inv(LMS_P_TO_IZAZBZ)

SURROUND = {
    'dark': (0.8, 0.525, 0.8),
    'dim': (0.9, 0.59, 0.9),
    'average': (1, 0.69, 1)
}

HUE_QUADRATURE = {
    # Red, Yellow, Green, Blue, Red
    "h": (33.44, 89.29, 146.30, 238.36, 393.44),
    "e": (0.68, 0.64, 1.52, 0.77, 0.68),
    "H": (0.0, 100.0, 200.0, 300.0, 400.0)
}


def hue_quadrature(h: float) -> float:
    """
    Hue to hue quadrature.

    https://onlinelibrary.wiley.com/doi/pdf/10.1002/col.22324
    """

    hp = util.constrain_hue(h)
    if hp <= HUE_QUADRATURE['h'][0]:
        hp += 360

    i = bisect.bisect_left(HUE_QUADRATURE['h'], hp) - 1
    hi, hii = HUE_QUADRATURE['h'][i:i + 2]
    ei, eii = HUE_QUADRATURE['e'][i:i + 2]
    Hi = HUE_QUADRATURE['H'][i]

    t = (hp - hi) / ei
    return Hi + (100 * t) / (t + (hii - hp) / eii)


def inv_hue_quadrature(Hz: float) -> float:
    """Hue quadrature to hue."""

    Hp = (Hz % 400 + 400) % 400
    i = math.floor(0.01 * Hp)
    Hp = Hp % 100
    hi, hii = HUE_QUADRATURE['h'][i:i + 2]
    ei, eii = HUE_QUADRATURE['e'][i:i + 2]

    return util.constrain_hue((Hp * (eii * hi - ei * hii) - 100 * hi * eii) / (Hp * (eii - ei) - 100 * eii))


def adapt(
    xyz_b: Vector,
    xyz_wb: Vector,
    xyz_wd: Vector,
    db: float,
    dd: float,
    xyz_wo: Vector = DEF_ILLUMINANT_BI
) -> Vector:
    """
    Use 2 step chromatic adaptation by Qiyan Zhai and Ming R. Luo using CAM02.

    https://opg.optica.org/oe/fulltext.cfm?uri=oe-26-6-7724&id=383537

    `xyz_b`: the sample color
    `xyz_wb`: input illuminant of the sample color
    `xyz_wd`: output illuminant
    `xyz_wo`: the baseline illuminant, by default we use equal energy.
    """

    yb = xyz_wb[1] / xyz_wo[1]
    yd = xyz_wd[1] / xyz_wo[1]

    rgb_b = alg.matmul_x3(CAT02, xyz_b, dims=alg.D2_D1)
    rgb_wb = alg.matmul_x3(CAT02, xyz_wb, dims=alg.D2_D1)
    rgb_wd = alg.matmul_x3(CAT02, xyz_wd, dims=alg.D2_D1)
    rgb_wo = alg.matmul_x3(CAT02, xyz_wo, dims=alg.D2_D1)

    d_rgb_wb = alg.add_x3(
        alg.multiply_x3(db * yb, alg.divide_x3(rgb_wo, rgb_wb, dims=alg.D1), dims=alg.SC_D1),
        1 - db,
        dims=alg.D1_SC
    )
    d_rgb_wd = alg.add_x3(
        alg.multiply_x3(dd * yd, alg.divide_x3(rgb_wo, rgb_wd, dims=alg.D1), dims=alg.SC_D1),
        1 - dd,
        dims=alg.D1_SC
    )
    d_rgb = alg.divide_x3(d_rgb_wb, d_rgb_wd, dims=alg.D1)
    rgb_d = alg.multiply_x3(d_rgb, rgb_b, dims=alg.D1)
    return alg.matmul_x3(CAT02_INV, rgb_d, dims=alg.D2_D1)


class Environment:
    """
    Class to calculate and contain any required environmental data (viewing conditions included).

    While originally for CIECAM models, the following applies to ZCAM as well.
    Usage Guidelines for CIECAM97s (Nathan Moroney)
    https://www.imaging.org/site/PDFS/Papers/2000/PICS-0-81/1611.pdf

    white: This is the (x, y) chromaticity points for the white point. ZCAM is designed to use D65.
        Generally, D65 should always be used, but we allow the possibility of variants of D65. This should
        be the same value as set in the color class `WHITE` value.

    ref_white: The reference white in XYZ scaled by 100.

    adapting_luminance: This is the luminance of the adapting field. The units are in cd/m2.
        The equation is `L = (E * R) / π`, where `E` is the illuminance in lux, `R` is the reflectance,
        and `L` is the luminance. If we assume a perfectly reflecting diffuser, `R` is assumed as 1.
        For the "gray world" assumption, we must also divide by 5 (or multiply by 0.2 - 20%).
        This results in `La = E / π * 0.2`. You can also ignore this gray world assumption converting
        lux directly to nits (cd/m2) `lux / π`.

    background_luminance: The background is the region immediately surrounding the stimulus and
        for images is the neighboring portion of the image. Generally, this value is set to a value of 20.
        This implicitly assumes a gray world assumption.

    surround: The surround is categorical and is defined based on the relationship between the relative
        luminance of the surround and the luminance of the scene or image white. While there are 4 defined
        surrounds, usually just `average`, `dim`, and `dark` are used.

        Dark    | 0%        | Viewing film projected in a dark room
        Dim     | 0% to 20% | Viewing television
        Average | > 20%     | Viewing surface colors

    discounting: Whether we are discounting the illuminance. Done when eye is assumed to be fully adapted.
    """

    def __init__(
        self,
        *,
        white: VectorLike,
        reference_white: VectorLike,
        adapting_luminance: float,
        background_luminance: float,
        surround: str,
        discounting: bool
    ):
        """
        Initialize environmental viewing conditions.

        Using the specified viewing conditions, and general environmental data,
        initialize anything that we can ahead of time to speed up the process.
        """

        self.output_white = util.xyz_to_absxyz(util.xy_to_xyz(white), yw=100)
        self.ref_white = [*reference_white]
        self.surround = surround
        self.discounting = discounting
        xyz_w = self.ref_white

        # The average luminance of the environment in `cd/m^2cd/m` (a.k.a. nits)
        self.la = adapting_luminance
        # The relative luminance of the nearby background
        self.yb = background_luminance
        # Absolute luminance of the reference white.
        yw = xyz_w[1]
        self.fb = math.sqrt(self.yb / yw)
        self.fl = 0.171 * alg.nth_root(self.la, 3) * (1 - math.exp((-48 / 9) * self.la))

        # Surround: dark, dim, and average
        f, self.c, _ = SURROUND[self.surround]
        self.fs = self.c
        self.epsilon = 3.7035226210190005e-11
        self.rho = 1.7 * 2523 / (2 ** 5)
        self.b = 1.15
        self.g = 0.66

        self.izw = xyz_to_izazbz(xyz_w, LMS_P_TO_IZAZBZ, self.rho)[0] - self.epsilon
        self.qzw = (
            2700 * alg.spow(self.izw, (1.6 * self.fs) / (self.fb ** 0.12)) *
            ((self.fs ** 2.2) * (self.fb ** 0.5) * (self.fl ** 0.2))
        )

        # Degree of adaptation calculating if not discounting illuminant (assumed eye is fully adapted)
        self.d = alg.clamp(f * (1 - 1 / 3.6 * math.exp((-self.la - 42) / 92)), 0, 1) if not self.discounting else 1


def zcam_to_xyz(
    Jz: float | None = None,
    Cz: float | None = None,
    hz: float | None = None,
    Qz: float | None = None,
    Mz: float | None = None,
    Sz: float | None = None,
    Vz: float | None = None,
    Kz: float | None = None,
    Wz: float | None = None,
    Hz: float | None = None,
    env: Environment | None = None
) -> Vector:
    """
    From ZCAM to XYZ.

    Reverse calculation can actually be obtained from a small subset of the ZCAM components
    Really, only one suitable value is needed for each type of attribute: (lightness/brightness),
    (chroma/colorfulness/saturation), (hue/hue quadrature). If more than one for a given
    category is given, we will fail as we have no idea which is the right one to use. Also,
    if none are given, we must fail as well as there is nothing to calculate with.
    """

    # These check ensure one, and only one attribute for a given category is provided.
    if not ((Jz is not None) ^ (Qz is not None)):
        raise ValueError("Conversion requires one and only one: 'Jz' or 'Qz'")

    if not (
        (Cz is not None) ^ (Mz is not None) ^ (Sz is not None) ^ (Vz is not None) ^ (Kz is not None) ^ (Wz is not None)
    ):
        raise ValueError("Conversion requires one and only one: 'Cz', 'Mz', 'Sz', 'Vz', 'Kz', or 'Wz'")

    # Hue is absolutely required
    if not ((hz is not None) ^ (Hz is not None)):
        raise ValueError("Conversion requires one and only one: 'hz' or 'Hz'")

    # We need viewing conditions
    if env is None:
        raise ValueError("No viewing conditions/environment provided")

    # Shortcut out if black?
    if Jz == 0.0 or Qz == 0.0:
        if not any((Cz, Mz, Sz, Vz, Kz, Wz)):
            return [0.0, 0.0, 0.0]

    # Break hue into Cartesian components
    h_rad = 0.0
    if hz is None:
        hz = inv_hue_quadrature(Hz)  # type: ignore[arg-type]
    h_rad = math.radians(hz % 360)
    cos_h = math.cos(h_rad)
    sin_h = math.sin(h_rad)
    hp = hz
    if hp <= HUE_QUADRATURE['h'][0]:
        hp += 360
    ez = 1.015 + math.cos(math.radians(89.038 + hp))

    # Calculate `iz` from one of the lightness derived coordinates.
    if Qz is None:
        Qz = (Jz * 0.01) * env.qzw  # type: ignore[operator]

    if Jz is None:
        Jz = 100 * (Qz / env.qzw)

    iz = alg.nth_root(
        Qz / ((env.fs ** 2.2) * (env.fb ** 0.5) * (env.fl ** 0.2) * 2700), (1.6 * env.fs) / (env.fb ** 0.12)
    )

    # Calculate `Mz` from the various chroma like parameters.
    if Sz is not None:
        Cz = Qz * Sz ** 2 / (100 * env.qzw * env.fl ** 1.2)
    elif Vz is not None:
        Cz = alg.nth_root((Vz ** 2 - (Jz - 58) ** 2) / 3.4, 2)
    elif Kz is not None:
        Cz = alg.nth_root((((Kz - 100) / - 0.8) ** 2 - (Jz ** 2)) / 8, 2)
    elif Wz is not None:
        Cz = alg.nth_root((Wz - 100) ** 2 - (100 - Jz) ** 2, 2)

    if Cz is not None:
        Mz = (Cz / 100) * env.qzw

    Czp = alg.spow(
        (Mz * (env.izw ** (0.78)) * (env.fb ** 0.1)) / (100 * (ez ** 0.068) * (env.fl ** 0.2)),
        1.0 / 0.37 / 2
    )

    # Convert back to XYZ
    az, bz = cos_h * Czp, sin_h * Czp
    iz += env.epsilon
    xyz_abs = izazbz_to_xyz([iz, az, bz], IZAZBZ_TO_LMS_P, env.rho)

    return util.absxyz_to_xyz(adapt(xyz_abs, env.output_white, env.ref_white, env.d, env.d))


def xyz_to_zcam(xyz: Vector, env: Environment, calc_hue_quadrature: bool = False) -> Vector:
    """From XYZ to ZCAM."""

    # Steps 4 - 7
    iz, az, bz = xyz_to_izazbz(
        adapt(util.xyz_to_absxyz(xyz), env.ref_white, env.output_white, env.d, env.d),
        LMS_P_TO_IZAZBZ,
        env.rho
    )

    # Step 8
    iz -= env.epsilon

    # Step 9
    hz = util.constrain_hue(math.degrees(math.atan2(bz, az)))

    # Step 10
    Hz = hue_quadrature(hz) if calc_hue_quadrature else alg.NaN

    # Step 11
    hp = hz
    if hp <= HUE_QUADRATURE['h'][0]:
        hp += 360
    ez = 1.015 + math.cos(math.radians(89.038 + hp))

    # Step 12
    Qz = (
        2700 * alg.spow(iz, (1.6 * env.fs) / (env.fb ** 0.12)) *
        ((env.fs ** 2.2) * (env.fb ** 0.5) * (env.fl ** 0.2))
    )

    # Step 13
    Jz = 100 * (Qz / env.qzw)

    # Step 14
    Mz = (
        100 * ((az ** 2 + bz ** 2) ** (0.37)) *
        ((alg.spow(ez, 0.068) * (env.fl ** 0.2)) / ((env.fb ** 0.1) * alg.spow(env.izw, 0.78)))
    )

    # Step 15
    Cz = 100 * (Mz / env.qzw)

    # Step 16
    Sz = 100 * (env.fl ** 0.6) * alg.nth_root(Mz / Qz, 2) if Qz else 0.0

    # Step 17
    Vz = math.sqrt((Jz - 58) ** 2 + 3.4 * (Cz ** 2))

    # Step 18
    Kz = 100 - 0.8 * math.sqrt(Jz ** 2 + 8 * (Cz ** 2))

    # Step 19
    Wz = 100 - math.sqrt((100 - Jz) ** 2 + Cz ** 2)

    return [Jz, Cz, hz, Qz, Mz, Sz, Vz, Kz, Wz, Hz]


def xyz_to_zcam_jmh(xyz: Vector, env: Environment) -> Vector:
    """XYZ to ZCAM JMh."""

    zcam = xyz_to_zcam(xyz, env)
    Jz, Mz, hz = zcam[0], zcam[4], zcam[2]
    return [Jz, Mz, hz]


def zcam_jmh_to_xyz(jmh: Vector, env: Environment) -> Vector:
    """ZCAM JMh to XYZ."""

    Jz, Mz, hz = jmh
    return zcam_to_xyz(Jz=Jz, Mz=Mz, hz=hz, env=env)


class ZCAMJMh(LCh):
    """ZCAM class (JMh)."""

    BASE = "xyz-d65"
    NAME = "zcam-jmh"
    SERIALIZE = ("--zcam-jmh",)
    CHANNEL_ALIASES = {
        "lightness": "jz",
        "colorfulness": 'mz',
        "hue": 'hz',
        'j': 'jz',
        'm': "mz",
        'h': 'hz'
    }
    WHITE = WHITES['2deg']['D65']
    DYNAMIC_RANGE = 'hdr'

    # Assuming sRGB which has a lux of 64
    ENV = Environment(
        # D65 white point.
        white=WHITE,
        # The reference white in XYZ scaled by 100
        reference_white=util.xyz_to_absxyz(util.xy_to_xyz(WHITE), 100),
        # Assuming sRGB which has a lux of 64: `((E * R) / PI)` where `R = 1`.
        # Divided by 5 (or multiplied by 20%) assuming gray world.
        adapting_luminance=64 / math.pi * 0.2,
        # 20% relative to an XYZ luminance of 100 (scaled by 100) for the gray world assumption.
        background_luminance=20,
        # Assume an average surround
        surround='average',
        # Do not discount illuminant.
        discounting=False
    )
    CHANNELS = (
        Channel("jz", 0.0, 100.0),
        Channel("mz", 0, 60.0),
        Channel("hz", 0.0, 360.0, flags=FLG_ANGLE)
    )

    def normalize(self, coords: Vector) -> Vector:
        """Normalize."""

        if coords[1] < 0.0:
            return self.from_base(self.to_base(coords))
        coords[2] %= 360.0
        return coords

    def hue_name(self) -> str:
        """Hue name."""

        return "hz"

    def radial_name(self) -> str:
        """Radial name."""

        return "mz"

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "jz"

    def to_base(self, coords: Vector) -> Vector:
        """From ZCAM JMh to XYZ."""

        return zcam_jmh_to_xyz(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to ZCAM JMh."""

        return xyz_to_zcam_jmh(coords, self.ENV)
