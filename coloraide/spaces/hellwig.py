"""
Hellwig 2022: CAM16 class (JMh) with corrections.

CAM16
https://www.researchgate.net/publication/318152296_Comprehensive_color_solutions_CAM16_CAT16_and_CAM16-UCS
https://www.researchgate.net/publication/220865484_Usage_guidelines_for_CIECAM97s
https://doi.org/10.1002/col.22131
https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067

CAM16 Corrections: Hellwig and Fairchild
http://markfairchild.org/PDFs/PAP45.pdf

Helmholtz Kohlrausch Effect extension: Hellwig, Stolitzka, and Fairchild
https://www.scribd.com/document/788387893/Color-Research-Application-2022-Hellwig-Extending-CIECAM02-and-CAM16-for-the-Helmholtz-Kohlrausch-effect
"""
from __future__ import annotations
import math
from .cam16 import (
    M16,
    MI6_INV,
    M1,
    adapt,
    unadapt,
    hue_quadrature,
    inv_hue_quadrature
)
from .cam16 import Environment as _Environment
from .lch import LCh
from .. import util
from .. import algebra as alg
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from ..types import Vector, VectorLike


def hue_angle_dependency(h: float) -> float:
    """Calculate the hue angle dependency for CAM16."""

    return (
        -0.160 * math.cos(h)
        + 0.132 * math.cos(2 * h)
        - 0.405 * math.sin(h)
        + 0.080 * math.sin(2 * h)
        + 0.792
    )


def eccentricity(h: float) -> float:
    """Calculate eccentricity."""

    # Eccentricity
    h2 = 2 * h
    h3 = 3 * h
    h4 = 4 * h
    return (
        -0.0582 * math.cos(h) - 0.0258 * math.cos(h2)
        - 0.1347 * math.cos(h3) + 0.0289 * math.cos(h4)
        -0.1475 * math.sin(h) - 0.0308 * math.sin(h2)
        + 0.0385 * math.sin(h3) + 0.0096 * math.sin(h4) + 1
    )


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

    `hk`: Whether to adjust lightness for the Helmholtz-Kohlrausch effect.
    """

    def __init__(
        self,
        *,
        white: VectorLike,
        adapting_luminance: float,
        background_luminance: float,
        surround: str,
        discounting: bool,
        hk: bool,
    ) -> None:
        """
        Initialize environmental viewing conditions.

        Using the specified viewing conditions, and general environmental data,
        initialize anything that we can ahead of time to speed up the process.
        """

        super().__init__(
            white=white,
            adapting_luminance=adapting_luminance,
            background_luminance=background_luminance,
            surround=surround,
            discounting=discounting
        )
        self.hk = hk

    def calculate_adaptation(self, xyz_w: Vector) -> None:
        """Calculate the adaptation of the reference point and related variables."""

        # Cone response for reference white
        self.rgb_w = alg.matmul_x3(M16, xyz_w, dims=alg.D2_D1)

        self.d_rgb = [alg.lerp(1, self.yw / coord, self.d) for coord in self.rgb_w]
        self.d_rgb_inv = [1 / coord for coord in self.d_rgb]

        # Achromatic response
        self.rgb_cw = alg.multiply_x3(self.rgb_w, self.d_rgb, dims=alg.D1)
        rgb_aw = adapt(self.rgb_cw, self.fl)
        self.a_w = (2 * rgb_aw[0] + rgb_aw[1] + 0.05 * rgb_aw[2])


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

    # Shortcut out if black?
    if J == 0.0 or Q == 0:
        if not any((C, M, s)):
            return [0.0, 0.0, 0.0]

    # Break hue into Cartesian components
    h_rad = 0.0
    if h is not None:
        h_rad = math.radians(h % 360)
    elif H is not None:
        h_rad = math.radians(inv_hue_quadrature(H))

    # Calculate `J_root` from one of the lightness derived coordinates.
    if M is not None:
        C = M * 35 / env.a_w
    elif C is not None:
        M = (C * env.a_w) / 35

    if env.hk and Q is not None:
        J = (50 * env.c * Q) / env.a_w

    if J is not None:
        if env.hk:
            if C is None:
                raise ValueError('C or M is required to resolve J and Q when H-K effect is enabled')
            J -= hue_angle_dependency(h_rad) * alg.spow(C, 0.587)
        Q = (2 / env.c) * (J / 100) * env.a_w
    elif Q is not None:
        J = (50 * env.c * Q) / env.a_w

    if s is not None:
        M = Q * (s / 100)  # type: ignore[operator]

    # Eccentricity
    et = eccentricity(h_rad)

    # Achromatic response
    A = env.a_w * alg.nth_root(J / 100, env.c * env.z)  # type: ignore[operator]

    # Calculate red-green and yellow-blue components
    cos_h = math.cos(h_rad)
    sin_h = math.sin(h_rad)
    p1 = 43 * env.nc * et
    p2 = A
    r = M / p1  # type: ignore[operator]
    a = r * cos_h
    b = r * sin_h

    # Calculate back from cone response to XYZ
    rgb_a = alg.multiply_x3(alg.matmul_x3(M1, [p2, a, b], dims=alg.D2_D1), 1 / 1403, dims=alg.D1_SC)
    rgb_c = unadapt(rgb_a, env.fl)
    return util.scale1(alg.matmul_x3(MI6_INV, alg.multiply_x3(rgb_c, env.d_rgb_inv, dims=alg.D1), dims=alg.D2_D1))


def xyz_to_cam(xyz: Vector, env: Environment, calc_hue_quadrature: bool = False) -> Vector:
    """From XYZ to CAM16."""

    # Calculate cone response
    rgb_c = alg.multiply_x3(
        alg.matmul_x3(M16, util.scale100(xyz), dims=alg.D2_D1),
        env.d_rgb,
        dims=alg.D1
    )
    rgb_a = adapt(rgb_c, env.fl)

    # Calculate red-green and yellow components and resultant hue
    p2 = 2 * rgb_a[0] + rgb_a[1] + 0.05 * rgb_a[2]
    a = rgb_a[0] + (-12 * rgb_a[1] + rgb_a[2]) / 11
    b = (rgb_a[0] + rgb_a[1] - 2 * rgb_a[2]) / 9
    h_rad = math.atan2(b, a) % math.tau

    # Eccentricity
    et = eccentricity(h_rad)

    # Achromatic response
    A = p2

    # Lightness
    J = 100 * alg.spow(A / env.a_w, env.c * env.z)

    # Brightness
    Q = (2 / env.c) * (J / 100) * env.a_w

    # Colorfulness
    M = 43 * env.nc * et * math.hypot(a, b)

    # Chroma
    C = 35 * (M / env.a_w)

    # Saturation
    s = 100 * alg.zdiv(M, Q)

    # Hue
    h = util.constrain_hue(math.degrees(h_rad))

    # Hue quadrature
    H = hue_quadrature(h) if calc_hue_quadrature else alg.NaN

    # Adjust lightness and brightness for the Helmholtz-Kohlrausch effect
    if env.hk:
        J += hue_angle_dependency(h_rad) * alg.spow(C, 0.587)
        Q = (2 / env.c) * (J / 100) * env.a_w

    return [J, C, h, s, Q, M, H]


def xyz_to_cam_jmh(xyz: Vector, env: Environment) -> Vector:
    """XYZ to CAM16 JMh with corrections."""

    cam16 = xyz_to_cam(xyz, env)
    J, M, h = cam16[0], cam16[5], cam16[2]
    return [J, M, h]


def cam_jmh_to_xyz(jmh: Vector, env: Environment) -> Vector:
    """CAM16 JMh with corrections to XYZ."""

    J, M, h = jmh
    return cam_to_xyz(J=J, M=M, h=h, env=env)


class HellwigJMh(LCh):
    """CAM16 class (JMh) with corrections."""

    BASE = "xyz-d65"
    NAME = "hellwig-jmh"
    SERIALIZE = ("--hellwig-jmh",)
    CHANNEL_ALIASES = {
        "lightness": "j",
        "colorfulness": 'm',
        "hue": 'h'
    }
    WHITE = WHITES['2deg']['D65']
    HK = False

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
        discounting=False,
        # Account for Helmholtz-Kohlrausch effect
        hk=False
    )
    CHANNELS = (
        Channel("j", 0.0, 100.0),
        Channel("m", 0, 70.0),
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
        """From CAM16 JMh to XYZ."""

        return cam_jmh_to_xyz(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16 JMh."""

        return xyz_to_cam_jmh(coords, self.ENV)


class HellwigHKJMh(HellwigJMh):
    """CAM16 class (JMh) with corrections and accounting for the Helmholtz-Kohlrausch effect."""

    NAME = "hellwig-hk-jmh"
    SERIALIZE = ("--hellwig-hk-jmh",)
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
        discounting=False,
        # Account for Helmholtz-Kohlrausch effect
        hk=True
    )
    CHANNELS = (
        Channel("j", 0.0, 101.56018891418564),
        Channel("m", 0, 70.0),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )
