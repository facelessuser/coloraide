"""
CAM16 class.

https://www.imaging.org/site/PDFS/Papers/2000/PICS-0-81/1611.pdf
https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067
https://doi.org/10.1002/col.22131
"""
from __future__ import annotations
import math
import bisect
from ..spaces import Space, Labish
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT
from .. import util
from .. import algebra as alg
from ..types import Vector, VectorLike
from typing import Optional, cast

# CAT16
M16 = [
    [0.401288, 0.650173, -0.051461],
    [-0.250268, 1.204414, 0.045854],
    [-0.002079, 0.048952, 0.953127]
]

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
        x = alg.npow(fl * c * 0.01, ADAPTED_COEF)
        adapted.append(400 * math.copysign(x, c) / (x + 27.13))
    return adapted


def unadapt(adapted: Vector, fl: float) -> Vector:
    """Remove adaptation from coordinates."""

    coords = []
    constant = 100 / fl * math.pow(27.13, ADAPTED_COEF_INV)
    for c in adapted:
        cabs = abs(c)
        coords.append(math.copysign(constant * alg.npow(cabs / (400 - cabs), ADAPTED_COEF_INV), c))
    return coords


class Environment:
    """
    Class to calculate and contain any required environmental data (viewing conditions included).

    Usage Guidelines for CIECAM97s (Nathan Moroney)
    https://www.imaging.org/site/PDFS/Papers/2000/PICS-0-81/1611.pdf

    ref_white: The reference white XYZ. We assume XYZ is in the range 0 - 1 as that is how ColorAide
        handles XYZ everywhere else. It will be scaled up to 0 - 100.

    adapting_luminance: This is the the luminance of the adapting field. The units are in cd/m2.
        The equation is `L = (E * R) / π`, where `E` is the illuminance in lux, `R` is the reflectance,
        and `L` is the luminance. If we assume a perfectly reflecting diffuser, `R` is assumed as 1.
        For the "gray world" assumption, we must also divide by 5 (or multiply by 0.2 - 20%).
        This results in `La = E / π * 0.2`.

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
        ref_white: VectorLike,
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
        self.ref_white = util.xy_to_xyz(ref_white)
        self.surround = surround
        xyz_w = alg.multiply(self.ref_white, 100, dims=alg.D1_SC)

        # The average luminance of the environment in `cd/m^2cd/m` (a.k.a. nits)
        self.la = adapting_luminance
        # The relative luminance of the nearby background
        self.yb = background_luminance
        # Absolute luminance of the reference white.
        yw = xyz_w[1]

        # Cone response for reference white
        rgb_w = alg.dot(M16, xyz_w)

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
        rgb_cw = alg.multiply(rgb_w, self.d_rgb, dims=alg.D1)
        rgb_aw = adapt(rgb_cw, self.fl)
        self.a_w = self.nbb * (2 * rgb_aw[0] + rgb_aw[1] + 0.05 * rgb_aw[2])


def cam16_to_xyz_d65(
    J: Optional[float] = None,
    C: Optional[float] = None,
    h: Optional[float] = None,
    s: Optional[float] = None,
    Q: Optional[float] = None,
    M: Optional[float] = None,
    H: Optional[float] = None,
    env: Optional[Environment] = None
) -> Vector:
    """From CAM16 to XYZ."""

    # Reverse calculation can actually be obtained from a small subset of the components
    # Really, only one should be given as we won't know which one is correct otherwise,
    # but we don't currently enforce it as we expect the `Space` object to do that.
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
    if J == 0 or Q == 0:
        return [0, 0, 0]

    # Break hue into Cartesian components
    h_rad = math.radians(h if h is not None else inv_hue_quadrature(cast(float, H)))
    cos_h = math.cos(h_rad)
    sin_h = math.sin(h_rad)

    # Calculate `J_root` from one of the lightness derived coordinates.
    if J is not None:
        J_root = alg.nth_root(J, 2) * 0.1
    else:
        J_root = 0.25 * env.c * cast(float, Q) / ((env.a_w + 4) * env.fl_root)

    # Calculate the `t` value from one of the chroma derived coordinates
    if C is not None:
        alpha = C / J_root
    elif M is not None:
        alpha = (M / env.fl_root) / J_root
    else:
        alpha = 0.0004 * (cast(float, s) ** 2) * (env.a_w + 4) / env.c
    t = alg.npow(alpha * math.pow(1.64 - math.pow(0.29, env.n), -0.73), 10 / 9)

    # Eccentricity
    et = 0.25 * (math.cos(h_rad + 2) + 3.8)

    # Achromatic response
    A = env.a_w * alg.npow(J_root, 2 / env.c / env.z)

    # Calculate red-green and yellow-blue components
    p1 = 5e4 / 13 * env.nc * env.ncb * et
    p2 = A / env.nbb
    r = 23 * (p2 + 0.305) * t / (23 * p1 + t * (11 * cos_h + 108 * sin_h))
    a = r * cos_h
    b = r * sin_h

    # Calculate back from cone response to XYZ
    rgb_c = unadapt(alg.multiply(alg.dot(M1, [p2, a, b], dims=alg.D2_D1), 1 / 1403, dims=alg.D1_SC), env.fl)
    return alg.divide(
        alg.dot(MI6_INV, alg.multiply(rgb_c, env.d_rgb_inv, dims=alg.D1), dims=alg.D2_D1),
        100,
        dims=alg.D1_SC
    )


def xyz_d65_to_cam16(xyzd65: Vector, env: Environment) -> Vector:
    """From XYZ to CAM16."""

    # Cone response
    rgb_a = adapt(
        alg.multiply(
            alg.dot(M16, alg.multiply(xyzd65, 100, dims=alg.D1_SC), dims=alg.D2_D1),
            env.d_rgb,
            dims=alg.D1
        ),
        env.fl
    )

    # Red-green and yellow-blue components
    a = rgb_a[0] + (-12 * rgb_a[1] + rgb_a[2]) / 11
    b = (rgb_a[0] + rgb_a[1] - 2 * rgb_a[2]) / 9
    h_rad = math.atan2(b, a)

    # Eccentricity
    et = 0.25 * (math.cos(h_rad + 2) + 3.8)

    t = (
        5e4 / 13 * env.nc * env.ncb * et * math.sqrt(a ** 2 + b ** 2) /
        (rgb_a[0] + rgb_a[1] + 1.05 * rgb_a[2] + 0.305)
    )
    alpha = alg.npow(t, 0.9) * math.pow(1.64 - math.pow(0.29, env.n), 0.73)

    # Achromatic response
    A = env.nbb * (2 * rgb_a[0] + rgb_a[1] + 0.05 * rgb_a[2])

    J_root = alg.npow(A / env.a_w, 0.5 * env.c * env.z)

    # Lightness
    J = 100 * alg.npow(J_root, 2)

    # Brightness
    Q = (4 / env.c * J_root * (env.a_w + 4) * env.fl_root)

    # Chroma
    C = alpha * J_root

    # Colorfulness
    M = C * env.fl_root

    # Hue
    h = util.constrain_hue(math.degrees(h_rad))

    # Hue quadrature
    H = hue_quadrature(h)

    # Saturation
    s = 50 * alg.nth_root(env.c * alpha / (env.a_w + 4), 2)

    return [J, C, h, s, Q, M, H]


def xyz_d65_to_cam16_jmh(xyzd65: Vector, env: Environment) -> Vector:
    """XYZ to CAM16 JMh."""

    cam16 = xyz_d65_to_cam16(xyzd65, env)
    return [cam16[0], cam16[5], cam16[2]]


def cam16_jmh_to_xyz_d65(jmh: Vector, env: Environment) -> Vector:
    """CAM16 JMh to XYZ."""

    J, M, h = jmh
    return cam16_to_xyz_d65(J=J, M=M, h=h, env=env)


def cam16_jmh_to_cam16_jab(jmh: Vector) -> Vector:
    """Translate a CAM16 JMh to Jab of the same viewing conditions."""

    J, M, h = jmh
    return [
        J,
        M * math.cos(math.radians(h)),
        M * math.sin(math.radians(h))
    ]


def cam16_jab_to_cam16_jmh(jab: Vector) -> Vector:
    """Translate a CAM16 Jab to JMh of the same viewing conditions."""

    J, a, b = jab
    if J <= 0.0:
        J = a = b = 0.0
    M = math.sqrt(a ** 2 + b ** 2)
    h = math.degrees(math.atan2(b, a))

    return [J, M, util.constrain_hue(h)]


def xyz_d65_to_cam16_jab(xyzd65: Vector, env: Environment) -> Vector:
    """XYZ to CAM16 Jab."""

    jmh = xyz_d65_to_cam16_jmh(xyzd65, env)
    return cam16_jmh_to_cam16_jab(jmh)


def cam16_jab_to_xyz_d65(jab: Vector, env: Environment) -> Vector:
    """CAM16 Jab to XYZ."""

    jmh = cam16_jab_to_cam16_jmh(jab)
    return cam16_jmh_to_xyz_d65(jmh, env=env)


class CAM16(Labish, Space):
    """CAM16 class (Jab)."""

    BASE = "xyz-d65"
    NAME = "cam16"
    SERIALIZE = ("--cam16",)
    CHANNELS = (
        Channel("j", 0.0, 100.0, limit=(0.0, None)),
        Channel("a", -90.0, 90.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -90.0, 90.0, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "lightness": "j"
    }
    WHITE = WHITES['2deg']['D65']
    # Assuming sRGB which has a lux of 64
    ENV = Environment(WHITE, 64 / math.pi * 0.2, 20, 'average', False)

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from CAM16."""

        return cam16_jab_to_xyz_d65(coords, env=self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16."""

        return xyz_d65_to_cam16_jab(coords, env=self.ENV)
