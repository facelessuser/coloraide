"""
CAM16 class (JMh).

https://www.researchgate.net/publication/318152296_Comprehensive_color_solutions_CAM16_CAT16_and_CAM16-UCS
https://www.researchgate.net/publication/220865484_Usage_guidelines_for_CIECAM97s
https://doi.org/10.1002/col.22131
https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067
"""
from __future__ import annotations
import math
import bisect
from .. import util
from .. import algebra as alg
from ..spaces import Space, LChish
from ..cat import WHITES, CAT16
from ..channels import Channel, FLG_ANGLE
from .lch import ACHROMATIC_THRESHOLD
from ..types import Vector, VectorLike

# CAT16
M16 = CAT16.MATRIX
MI6_INV = alg.inv(M16)

M1 = [
    [460.0, 451.0, 288.0],
    [460.0, -891.0, -261.0],
    [460.0, -220.0, -6300.0]
]

ADAPTED_COEF = 0.42
ADAPTED_COEF_INV = 1 / ADAPTED_COEF

SURROUND = {
    'dark': (0.8, 0.525, 0.8),
    'dim': (0.9, 0.59, 0.9),
    'average': (1, 0.69, 1)
}

HUE_QUADRATURE = {
    # Red, Yellow, Green, Blue, Red
    "h": (20.14, 90.00, 164.25, 237.53, 380.14),
    "e": (0.8, 0.7, 1.0, 1.2, 0.8),
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


def inv_hue_quadrature(H: float) -> float:
    """Hue quadrature to hue."""

    Hp = (H % 400 + 400) % 400
    i = math.floor(0.01 * Hp)
    Hp = Hp % 100
    hi, hii = HUE_QUADRATURE['h'][i:i + 2]
    ei, eii = HUE_QUADRATURE['e'][i:i + 2]

    return util.constrain_hue((Hp * (eii * hi - ei * hii) - 100 * hi * eii) / (Hp * (eii - ei) - 100 * eii))


def adapt(coords: Vector, fl: float) -> Vector:
    """Adapt the coordinates."""

    adapted = []
    for c in coords:
        x = (fl * abs(c) * 0.01) ** ADAPTED_COEF
        adapted.append(400 * math.copysign(x, c) / (x + 27.13))
    return adapted


def unadapt(adapted: Vector, fl: float) -> Vector:
    """Remove adaptation from coordinates."""

    coords = []
    constant = 100 / fl * (27.13 ** ADAPTED_COEF_INV)
    for c in adapted:
        cabs = abs(c)
        coords.append(math.copysign(constant * alg.spow(cabs / (400 - cabs), ADAPTED_COEF_INV), c))
    return coords


class Environment:
    """
    Class to calculate and contain any required environmental data (viewing conditions included).

    Usage Guidelines for CIECAM97s (Nathan Moroney)
    https://www.researchgate.net/publication/220865484_Usage_guidelines_for_CIECAM97s

    white: This is the (x, y) chromaticity points for the white point. This should be the same
        value as set in the color class `WHITE` value.

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

        self.discounting = discounting
        self.ref_white = util.xy_to_xyz(white)
        self.surround = surround

        # The average luminance of the environment in `cd/m^2cd/m` (a.k.a. nits)
        self.la = adapting_luminance
        # The relative luminance of the nearby background
        self.yb = background_luminance
        # Absolute luminance of the reference white.
        xyz_w = util.scale100(self.ref_white)
        yw = xyz_w[1]

        # Cone response for reference white
        rgb_w = alg.matmul_x3(M16, xyz_w, dims=alg.D2_D1)

        # Surround: dark, dim, and average
        f, self.c, self.nc = SURROUND[self.surround]

        k = 1 / (5 * self.la + 1)
        k4 = k ** 4

        # Factor of luminance level adaptation
        self.fl = (k4 * self.la + 0.1 * (1 - k4) * (1 - k4) * math.pow(5 * self.la, 1 / 3))
        self.fl_root = math.pow(self.fl, 0.25)

        self.n = self.yb / yw
        self.z = 1.48 + math.sqrt(self.n)
        self.nbb = 0.725 * math.pow(self.n, -0.2)
        self.ncb = self.nbb

        # Degree of adaptation calculating if not discounting illuminant (assumed eye is fully adapted)
        d = alg.clamp(f * (1 - 1 / 3.6 * math.exp((-self.la - 42) / 92)), 0, 1) if not discounting else 1
        self.d_rgb = [alg.lerp(1, yw / coord, d) for coord in rgb_w]
        self.d_rgb_inv = [1 / coord for coord in self.d_rgb]

        # Achromatic response
        rgb_cw = alg.multiply_x3(rgb_w, self.d_rgb, dims=alg.D1)
        rgb_aw = adapt(rgb_cw, self.fl)
        self.a_w = self.nbb * (2 * rgb_aw[0] + rgb_aw[1] + 0.05 * rgb_aw[2])


def cam16_to_xyz_d65(
    J: float | None = None,
    C: float | None = None,
    h: float | None = None,
    s: float | None = None,
    Q: float | None = None,
    M: float | None = None,
    H: float | None = None,
    env: Environment | None = None
) -> Vector:
    """
    From CAM16 to XYZ.

    Reverse calculation can actually be obtained from a small subset of the CAM16 components
    Really, only one suitable value is needed for each type of attribute: (lightness/brightness),
    (chroma/colorfulness/saturation), (hue/hue quadrature). If more than one for a given
    category is given, we will fail as we have no idea which is the right one to use. Also,
    if none are given, we must fail as well as there is nothing to calculate with.
    """

    # These check ensure one, and only one attribute for a given category is provided.
    if not ((J is not None) ^ (Q is not None)):
        raise ValueError("Conversion requires one and only one: 'J' or 'Q'")

    if not ((C is not None) ^ (M is not None) ^ (s is not None)):
        raise ValueError("Conversion requires one and only one: 'C', 'M' or 's'")

    # Hue is absolutely required
    if not ((h is not None) ^ (H is not None)):
        raise ValueError("Conversion requires one and only one: 'h' or 'H'")

    # We need viewing conditions
    if env is None:
        raise ValueError("No viewing conditions/environment provided")

    # Black
    if J == 0.0 or Q == 0.0:
        return [0.0, 0.0, 0.0]

    # Break hue into Cartesian components
    h_rad = 0.0
    if h is not None:
        h_rad = math.radians(h % 360)
    elif H is not None:
        h_rad = math.radians(inv_hue_quadrature(H))
    cos_h = math.cos(h_rad)
    sin_h = math.sin(h_rad)

    # Calculate `J_root` from one of the lightness derived coordinates.
    J_root = 0.0
    if J is not None:
        J_root = alg.nth_root(J, 2) * 0.1
    elif Q is not None:
        J_root = 0.25 * env.c * Q / ((env.a_w + 4) * env.fl_root)

    # Calculate the `t` value from one of the chroma derived coordinates
    alpha = 0.0
    if C is not None:
        alpha = C / J_root
    elif M is not None:
        alpha = (M / env.fl_root) / J_root
    elif s is not None:
        alpha = 0.0004 * (s ** 2) * (env.a_w + 4) / env.c
    t = alg.spow(alpha * math.pow(1.64 - math.pow(0.29, env.n), -0.73), 10 / 9)

    # Eccentricity
    et = 0.25 * (math.cos(h_rad + 2) + 3.8)

    # Achromatic response
    A = env.a_w * alg.spow(J_root, 2 / env.c / env.z)

    # Calculate red-green and yellow-blue components
    p1 = 5e4 / 13 * env.nc * env.ncb * et
    p2 = A / env.nbb
    r = 23 * (p2 + 0.305) * alg.zdiv(t, 23 * p1 + t * (11 * cos_h + 108 * sin_h))
    a = r * cos_h
    b = r * sin_h

    # Calculate back from cone response to XYZ
    rgb_c = unadapt(alg.multiply_x3(alg.matmul_x3(M1, [p2, a, b], dims=alg.D2_D1), 1 / 1403, dims=alg.D1_SC), env.fl)
    return util.scale1(alg.matmul_x3(MI6_INV, alg.multiply_x3(rgb_c, env.d_rgb_inv, dims=alg.D1), dims=alg.D2_D1))


def xyz_d65_to_cam16(xyzd65: Vector, env: Environment, calc_hue_quadrature: bool = False) -> Vector:
    """From XYZ to CAM16."""

    # Cone response
    rgb_a = adapt(
        alg.multiply_x3(
            alg.matmul_x3(M16, util.scale100(xyzd65), dims=alg.D2_D1),
            env.d_rgb,
            dims=alg.D1
        ),
        env.fl
    )

    # Calculate hue from red-green and yellow-blue components
    a = rgb_a[0] + (-12 * rgb_a[1] + rgb_a[2]) / 11
    b = (rgb_a[0] + rgb_a[1] - 2 * rgb_a[2]) / 9
    h_rad = math.atan2(b, a) % math.tau

    # Eccentricity
    et = 0.25 * (math.cos(h_rad + 2) + 3.8)

    t = (
        5e4 / 13 * env.nc * env.ncb *
        alg.zdiv(et * math.sqrt(a ** 2 + b ** 2), rgb_a[0] + rgb_a[1] + 1.05 * rgb_a[2] + 0.305)
    )
    alpha = alg.spow(t, 0.9) * math.pow(1.64 - math.pow(0.29, env.n), 0.73)

    # Achromatic response
    A = env.nbb * (2 * rgb_a[0] + rgb_a[1] + 0.05 * rgb_a[2])

    J_root = alg.spow(A / env.a_w, 0.5 * env.c * env.z)

    # Lightness
    J = 100 * alg.spow(J_root, 2)

    # Brightness
    Q = (4 / env.c * J_root * (env.a_w + 4) * env.fl_root)

    # Chroma
    C = alpha * J_root

    # Colorfulness
    M = C * env.fl_root

    # Hue
    h = util.constrain_hue(math.degrees(h_rad))

    # Hue quadrature
    H = hue_quadrature(h) if calc_hue_quadrature else alg.NaN

    # Saturation
    s = 50 * alg.nth_root(env.c * alpha / (env.a_w + 4), 2)

    return [J, C, h, s, Q, M, H]


def xyz_d65_to_cam16_jmh(xyzd65: Vector, env: Environment) -> Vector:
    """XYZ to CAM16 JMh."""

    cam16 = xyz_d65_to_cam16(xyzd65, env)
    J, M, h = cam16[0], cam16[5], cam16[2]
    return [J, M, h]


def cam16_jmh_to_xyz_d65(jmh: Vector, env: Environment) -> Vector:
    """CAM16 JMh to XYZ."""

    J, M, h = jmh
    return cam16_to_xyz_d65(J=J, M=M, h=h, env=env)


class CAM16JMh(LChish, Space):
    """CAM16 class (JMh)."""

    BASE = "xyz-d65"
    NAME = "cam16-jmh"
    SERIALIZE = ("--cam16-jmh",)
    CHANNEL_ALIASES = {
        "lightness": "j",
        "colorfulness": 'm',
        "hue": 'h'
    }
    WHITE = WHITES['2deg']['D65']
    # Assuming sRGB which has a lux of 64: `((E * R) / PI) / 5` where `R = 1`.
    ENV = Environment(
        # Our white point.
        white=WHITE,
        # Assuming sRGB which has a lux of 64: `((E * R) / PI)` where `R = 1`.
        # Divided by 5 (or multiplied by 20%) assuming gray world.
        adapting_luminance=64 / math.pi * 0.2,
        # Gray world assumption, 20% of reference white's `Yw = 100`.
        background_luminance=20,
        # Average surround
        surround='average',
        # Do not discount illuminant
        discounting=False
    )
    CHANNELS = (
        Channel("j", 0.0, 100.0),
        Channel("m", 0, 105.0),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )

    def normalize(self, coords: Vector) -> Vector:
        """Normalize."""

        if coords[1] < 0.0:
            return self.from_base(self.to_base(coords))
        coords[2] %= 360.0
        return coords

    def is_achromatic(self, coords: Vector) -> bool | None:
        """Check if color is achromatic."""

        # Account for both positive and negative chroma
        return coords[0] == 0 or abs(coords[1]) < ACHROMATIC_THRESHOLD

    def to_base(self, coords: Vector) -> Vector:
        """From CAM16 JMh to XYZ."""

        return cam16_jmh_to_xyz_d65(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16 JMh."""

        return xyz_d65_to_cam16_jmh(coords, self.ENV)
