"""
CAM02 class (JMh).

https://www.researchgate.net/publication/318152296_Comprehensive_color_solutions_CAM16_CAT16_and_CAM16-UCS
https://en.wikipedia.org/wiki/CIECAM02
https://www.researchgate.net/publication/221501922_The_CIECAM02_color_appearance_model
https://arxiv.org/abs/1802.06067
"""
from __future__ import annotations
import math
from .. import util
from .. import algebra as alg
from .lch import LCh
from ..cat import WHITES, CAT02
from ..channels import Channel, FLG_ANGLE
from ..types import Vector
from .cam16 import (
    M1,
    hue_quadrature,
    inv_hue_quadrature,
    eccentricity,
    adapt,
    unadapt
)
from .cam16 import Environment as _Environment

# CAT02
M02 = CAT02.MATRIX
M02_INV = [
    [1.0961238208355142, -0.27886900021828726, 0.18274517938277304],
    [0.45436904197535916, 0.4735331543074118, 0.07209780371722913],
    [-0.009627608738429355, -0.00569803121611342, 1.0153256399545427]
]

XYZ_TO_HPE = [
    [0.38971, 0.68898, -0.07868],
    [-0.22981, 1.18340, 0.04641],
    [0.00000, 0.00000, 1.00000],
]

HPE_TO_XYZ = [
    [1.910196834052035, -1.1121238927878747, 0.20190795676749937],
    [0.3709500882486886, 0.6290542573926132, -8.055142184361326e-06],
    [0.0, 0.0, 1.0]
]


class Environment(_Environment):
    """
    Class to calculate and contain any required environmental data (viewing conditions included).

    Usage Guidelines for CIECAM97s (Nathan Moroney)
    https://www.researchgate.net/publication/220865484_Usage_guidelines_for_CIECAM97s

    `white`: This is the (x, y) chromaticity points for the white point. This should be the same
        value as set in the color class `WHITE` value.

    `adapting_luminance`: This is the luminance of the adapting field. The units are in cd/m2.
        The equation is `L = (E * R) / π`, where `E` is the illuminance in lux, `R` is the reflectance,
        and `L` is the luminance. If we assume a perfectly reflecting diffuser, `R` is assumed as 1.
        For the "gray world" assumption, we must also divide by 5 (or multiply by 0.2 - 20%).
        This results in `La = E / π * 0.2`. You can also ignore this gray world assumption converting
        lux directly to nits (cd/m2) `lux / π`.

    `background_luminance`: The background is the region immediately surrounding the stimulus and
        for images is the neighboring portion of the image. Generally, this value is set to a value of 20.
        This implicitly assumes a gray world assumption.

    `surround`: The surround is categorical and is defined based on the relationship between the relative
        luminance of the surround and the luminance of the scene or image white. While there are 4 defined
        surrounds, usually just `average`, `dim`, and `dark` are used.

        Dark    | 0%        | Viewing film projected in a dark room
        Dim     | 0% to 20% | Viewing television
        Average | > 20%     | Viewing surface colors

    `discounting`: Whether we are discounting the illuminance. Done when eye is assumed to be fully adapted.
    """

    def calculate_adaptation(self, xyz_w: Vector) -> None:
        """Calculate the adaptation of the reference point and related variables."""

        # Cone response for reference white
        self.rgb_w = alg.matmul_x3(M02, xyz_w, dims=alg.D2_D1)

        self.d_rgb = [(self.yw * (self.d / coord) + 1 - self.d) for coord in self.rgb_w]
        self.d_rgb_inv = [1 / coord for coord in self.d_rgb]
        self.rgb_cw = alg.multiply_x3(self.d_rgb, self.rgb_w, dims=alg.D1)
        self.rgb_pw = alg.matmul_x3(alg.matmul_x3(XYZ_TO_HPE, M02_INV), self.rgb_cw)

        # Achromatic response
        rgb_aw = adapt(self.rgb_pw, self.fl)
        self.a_w = self.nbb * (2 * rgb_aw[0] + rgb_aw[1] + 0.05 * rgb_aw[2])


def cam_to_xyz(
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
    From CAM02 to XYZ.

    Reverse calculation can actually be obtained from a small subset of the CAM02 components
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

    # Black?
    if J == 0.0:
        J = alg.EPS
        if not any((C, M, s)):
            return [0.0, 0.0, 0.0]
    if Q == 0.0:
        Q = alg.EPS
        if not any((C, M, s)):
            return [0.0, 0.0, 0.0]

    # Break hue into Cartesian components
    h_rad = 0.0
    if h is not None:
        h_rad = math.radians(h % 360)
    elif H is not None:
        h_rad = math.radians(inv_hue_quadrature(H))

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
    et = eccentricity(h_rad)

    # Achromatic response
    A = env.a_w * alg.spow(J_root, 2 / env.c / env.z)

    # Calculate red-green and yellow-blue components from hue
    cos_h = math.cos(h_rad)
    sin_h = math.sin(h_rad)
    p1 = 5e4 / 13 * env.nc * env.ncb * et
    p2 = A / env.nbb
    r = 23 * (p2 + 0.305) * alg.zdiv(t, 23 * p1 + t * (11 * cos_h + 108 * sin_h))
    a = r * cos_h
    b = r * sin_h

    # Calculate back from cone response to XYZ
    rgb_a = alg.multiply_x3(alg.matmul_x3(M1, [p2, a, b], dims=alg.D2_D1), 1 / 1403, dims=alg.D1_SC)
    rgb_c = alg.matmul_x3(alg.matmul_x3(M02, HPE_TO_XYZ, dims=alg.D2), unadapt(rgb_a, env.fl), dims=alg.D2_D1)
    return util.scale1(alg.matmul_x3(M02_INV, alg.multiply_x3(rgb_c, env.d_rgb_inv, dims=alg.D1), dims=alg.D2_D1))


def xyz_to_cam(xyz: Vector, env: Environment, calc_hue_quadrature: bool = False) -> Vector:
    """From XYZ to CAM02."""

    # Calculate cone response
    rgb_c = alg.multiply_x3(
        env.d_rgb,
        alg.matmul_x3(M02, util.scale100(xyz), dims=alg.D2_D1),
        dims=alg.D1
    )
    rgb_a = adapt(alg.matmul_x3(alg.matmul_x3(XYZ_TO_HPE, M02_INV, dims=alg.D2), rgb_c, dims=alg.D2_D1), env.fl)

    # Calculate red-green and yellow components and resultant hue
    p2 = 2 * rgb_a[0] + rgb_a[1] + 0.05 * rgb_a[2]
    a = rgb_a[0] + (-12 * rgb_a[1] + rgb_a[2]) / 11
    b = (rgb_a[0] + rgb_a[1] - 2 * rgb_a[2]) / 9
    u = rgb_a[0] + rgb_a[1] + 1.05 * rgb_a[2]
    h_rad = math.atan2(b, a) % math.tau

    # Eccentricity
    et = eccentricity(h_rad)

    # Calculate `t` so we can calculate `alpha`
    p1 = 5e4 / 13 * env.nc * env.ncb * et
    t = alg.zdiv(p1 * math.sqrt(a ** 2 + b ** 2), u + 0.305)
    alpha = alg.spow(t, 0.9) * math.pow(1.64 - math.pow(0.29, env.n), 0.73)

    # Achromatic response
    A = env.nbb * p2

    # Lightness
    J = 100 * alg.spow(A / env.a_w, env.c * env.z)
    J_root = alg.nth_root(J / 100, 2)

    # Brightness
    Q = (4 / env.c * J_root * (env.a_w + 4) * env.fl_root)

    # Chroma
    C = alpha * J_root

    # Colorfulness
    M = C * env.fl_root

    # Saturation
    s = 50 * alg.nth_root(env.c * alpha / (env.a_w + 4), 2)

    # Hue
    h = util.constrain_hue(math.degrees(h_rad))

    # Hue quadrature
    H = hue_quadrature(h) if calc_hue_quadrature else alg.NaN

    return [J, C, h, s, Q, M, H]


def xyz_to_cam_jmh(xyz: Vector, env: Environment) -> Vector:
    """XYZ to CAM02 JMh."""

    cam = xyz_to_cam(xyz, env)
    J, M, h = cam[0], cam[5], cam[2]
    return [J, M, h]


def cam_jmh_to_xyz(jmh: Vector, env: Environment) -> Vector:
    """CAM02 JMh to XYZ."""

    J, M, h = jmh
    return cam_to_xyz(J=J, M=M, h=h, env=env)


class CAM02JMh(LCh):
    """CAM02 class (JMh)."""

    BASE = "xyz-d65"
    NAME = "cam02-jmh"
    SERIALIZE = ("--cam02-jmh",)
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
        Channel("m", 0, 120.0),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "j"

    def radial_name(self) -> str:
        """Get radial name."""

        return "m"

    def normalize(self, coords: Vector) -> Vector:
        """Normalize."""

        if coords[1] < 0.0:
            return self.from_base(self.to_base(coords))
        coords[2] %= 360.0
        return coords

    def to_base(self, coords: Vector) -> Vector:
        """From CAM02 JMh to XYZ."""

        return cam_jmh_to_xyz(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM02 JMh."""

        return xyz_to_cam_jmh(coords, self.ENV)
