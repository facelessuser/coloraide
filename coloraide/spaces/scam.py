"""
Simple Color Appearance Model (sCAM).

https://opg.optica.org/oe/fulltext.cfm?uri=oe-32-3-3100&id=545619
"""
from __future__ import annotations
import math
from .. import util
from .. import algebra as alg
from .lch import LCh
from ..channels import Channel, FLG_ANGLE
from .cam16 import hue_quadrature, inv_hue_quadrature, M16, M16_INV
from .sucs import xyz_to_sucs, sucs_to_xyz
from ..cat import WHITES
from ..types import Vector, VectorLike

SURROUND = {
    'dark': (0.39, 0.85),
    'dim': (0.5, 0.95),
    'average': (0.52, 1)
}

HUE_QUADRATURE = {
    # Red, Yellow, Green, Blue, Red
    "h": (15.6, 80.3, 157.8, 219.7, 376.6),
    "e": (0.7, 0.6, 1.2, 0.9, 0.7),
    "H": (0.0, 100.0, 200.0, 300.0, 400.0)
}


def eccentricity(h: float) -> float:
    """Calculate eccentricity."""

    return 1 + 0.06 * math.cos(math.radians(110 + h))


def adapt(xyz: Vector, xyz_ws: Vector, xyz_wd: Vector, d: float) -> Vector:
    """
    Adapt using CAT16 matrix but using CAM02 degree of adaptation.

    This was proposed by one of the authors Li, Molin in the Colour project:
    https://github.com/colour-science/colour/pull/1349#issuecomment-3058339414
    """

    lms = alg.matmul_x3(M16, xyz, dims=alg.D2_D1)
    lms_ws = alg.matmul_x3(M16, xyz_ws, dims=alg.D2_D1)
    lms_wd = alg.matmul_x3(M16, xyz_wd, dims=alg.D2_D1)

    y_ratio = xyz_ws[1] / xyz_wd[1]
    lms_r = alg.divide_x3(lms_wd, lms_ws, dims=alg.D1)
    lms_a = [lms[r] * (d * y_ratio * lms_r[r] + (1 - d)) for r in range(3)]
    return alg.matmul_x3(M16_INV, lms_a, dims=alg.D2_D1)


class Environment:
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
        self.input_white = util.scale100(self.ref_white)
        self.yw = self.input_white[1]
        # Destination luminance
        self.output_white = alg.multiply_x3(
            util.xy_to_xyz(WHITES['2deg']['D65']),
            (self.la * 100) / self.yb,
            dims=alg.D1_SC
        )

        # Surround: dark, dim, and average
        self.c, self.fm = SURROUND[self.surround]

        self.fl = 0.1710 * (self.la ** (1 / 3)) * (1 / (1 - 0.4934 * math.exp(-0.9934 * self.la)))
        self.n = self.yb / self.yw
        self.z = 1.48 + math.sqrt(self.n)
        self.cz = self.c * self.z

        # Factor of luminance level adaptation
        self.d = alg.clamp(self.fm * (1 - 1 / 3.6 * math.exp((-self.la - 42) / 92)), 0, 1) if not discounting else 1


def scam_to_xyz(
    J: float | None = None,
    C: float | None = None,
    h: float | None = None,
    Q: float | None = None,
    M: float | None = None,
    D: float | None = None,
    V: float | None = None,
    W: float | None = None,
    K: float | None = None,
    H: float | None = None,
    env: Environment | None = None
) -> Vector:
    """
    From sCAM to XYZ.

    Reverse calculation can actually be obtained from a small subset of the sCAM components
    Really, only one suitable value is needed for each type of attribute: (lightness/brightness),
    (chroma/colorfulness/depth/vividness/whiteness/blackness), (hue/hue quadrature). If more than one for a given
    category is given, we will fail as we have no idea which is the right one to use. Also,
    if none are given, we must fail as well as there is nothing to calculate with.
    """

    # These check ensure one, and only one attribute for a given category is provided.
    if not ((J is not None) ^ (Q is not None)):
        raise ValueError("Conversion requires one and only one: 'J' or 'Q'")

    if not ((C is not None) ^ (M is not None) ^ (D is not None) ^ (V is not None) ^ (W is not None) ^ (K is not None)):
        raise ValueError("Conversion requires one and only one: 'C', 'M', 'D', 'V', 'W', 'K'")

    # Hue is absolutely required
    if not ((h is not None) ^ (H is not None)):
        raise ValueError("Conversion requires one and only one: 'h' or 'H'")

    # We need viewing conditions
    if env is None:
        raise ValueError("No viewing conditions/environment provided")

    # Calculate hue
    if h is not None:
        h = h % 360
    elif H is not None:
        h = inv_hue_quadrature(H)

    # Calculate `I` from one of the lightness derived coordinates.
    Ia = 0.0
    if J is not None:
        Ia = J
    elif Q is not None:
        Ia = Q / ((2 * (env.fl ** 0.46)) / env.c)
    I = alg.nth_root(Ia * 0.01, env.cz) * 100

    # Calculate the chroma component
    if W is not None:
        D = 100 - W
    elif K is not None:
        V = 100 - K
    if D is not None:
        C = alg.nth_root(((D / 1.3) ** 2 - (100 - Ia) ** 2) / 1.6, 2)
    elif V is not None:
        C = alg.nth_root((V ** 2 - Ia ** 2) / 3, 2)
    elif M is not None:
        et = eccentricity(h)  # type: ignore[arg-type]
        C = M * alg.spow(Ia, 0.27) / ((env.fl ** 0.1) * et * env.fm)

    # Convert to XYZ from sUCS
    xyz = sucs_to_xyz([I, C, h])  # type: ignore[list-item]

    # Apply chromatic adaptation
    return adapt(xyz, env.output_white, env.input_white, env.d)


def xyz_to_scam(xyz: Vector, env: Environment, calc_hue_quadrature: bool = True) -> Vector:
    """From XYZ to sCAM."""

    # Apply chromatic adaptation
    xyz = adapt(xyz, env.input_white, env.output_white, env.d)

    # Convert from XYZ to sUCS
    I, C, h = xyz_to_sucs(xyz)

    # Eccentricity
    et = eccentricity(h)

    # Lightness
    Ia = 100 * alg.spow(I * 0.01, env.cz)

    # Brightness
    Q = Ia * ((2 * (env.fl ** 0.46)) / env.c)

    # Colorfulness
    M = (C * (env.fl ** 0.1) * et) * alg.zdiv(1, alg.spow(Ia, 0.27), 0.0) * env.fm

    # Depth
    D = 1.3 * math.sqrt((100 - Ia) ** 2 + 1.6 * C ** 2)

    # Vividness
    V = math.sqrt(Ia ** 2 + 3 * C ** 2)

    # Whiteness
    W = 100 - D

    # Blackness
    K = 100 - V

    # Hue quadrature if required
    H = hue_quadrature(h) if calc_hue_quadrature else alg.NaN

    return [Ia, C, h, Q, M, D, V, W, K, H]


def xyz_to_scam_jmh(xyz: Vector, env: Environment) -> Vector:
    """XYZ to sCAM JMh."""

    scam = xyz_to_scam(xyz, env)
    return [scam[0], scam[4], scam[2]]


def scam_jmh_to_xyz(jmh: Vector, env: Environment) -> Vector:
    """Convert sCAM JMh to XYZ."""

    J, M, h = jmh
    return scam_to_xyz(J=J, M=M, h=h, env=env)


class sCAMJMh(LCh):
    """sCAM class (JMh)."""

    BASE = "xyz-d65"
    NAME = "scam-jmh"
    SERIALIZE = ("--scam-jmh",)
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
        Channel("m", 0, 25.0),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "j"

    def radial_name(self) -> str:
        """Get radial name."""

        return "m"

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return coords[0] == 0.0 or abs(coords[1]) < self.achromatic_threshold

    def normalize(self, coords: Vector) -> Vector:
        """Normalize."""

        if coords[1] < 0.0:
            return self.from_base(self.to_base(coords))
        coords[2] %= 360.0
        return coords

    def to_base(self, coords: Vector) -> Vector:
        """From sCAM JMh to XYZ."""

        return scam_jmh_to_xyz(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to sCAM JMh."""

        return xyz_to_scam_jmh(coords, self.ENV)
