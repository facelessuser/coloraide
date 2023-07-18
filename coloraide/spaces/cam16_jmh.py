"""
CAM16 class (JMh).

https://www.imaging.org/site/PDFS/Papers/2000/PICS-0-81/1611.pdf
https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067
https://doi.org/10.1002/col.22131
"""
from __future__ import annotations
import math
import bisect
from .. import util
from .. import algebra as alg
from ..spaces import Space, LChish
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .achromatic import Achromatic as _Achromatic
from .srgb_linear import lin_srgb_to_xyz
from .srgb import lin_srgb
from ..types import Vector, VectorLike
from typing import Any

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

ACHROMATIC_RESPONSE = [
    [0.5197637353103578, 0.10742101902546783, 209.53702017876432],
    [0.7653410752577902, 0.1428525220483835, 209.53699586564701],
    [0.9597225272459006, 0.1674639325209385, 209.5369779985614],
    [1.1268800051398011, 0.18685008110835863, 209.5369633468102],
    [1.2763267654963262, 0.2030639541700499, 209.53695070009815],
    [1.8790377054651906, 0.2606154320772664, 209.53690294574977],
    [2.3559753209404573, 0.2998668559412108, 209.53686786031403],
    [2.7660324716814633, 0.3305058430743194, 209.536839093849],
    [3.1325805945142164, 0.3559891904115732, 209.53681426762876],
    [3.4678031173571573, 0.37799038189311784, 209.53679218878383],
    [3.77902862541972, 0.3974595006625645, 209.53677216077193],
    [4.071081036208187, 0.41499276041597405, 209.53675373607226],
    [4.35987940988476, 0.4317047383578854, 209.53673583657556],
    [4.653923368359191, 0.44814375233486375, 209.53671791170922],
    [7.833618587426542, 0.5996289140723938, 209.53653852944092],
    [11.379933581738413, 0.73419775817062, 209.5363590374096],
    [15.226965773377025, 0.8572590366765755, 209.53617955383942],
    [19.331425543357224, 0.9717687075452716, 209.53600014937],
    [23.662223781347393, 1.0795574256327514, 209.5358208710024],
    [28.195712492409086, 1.181856050998015, 209.5356417521982],
    [32.91316356733728, 1.2795417603936534, 209.53546281794735],
    [37.799294675334956, 1.3732674055098613, 209.53528408756415],
    [42.841343691205466, 1.4635354939944947, 209.5351055763844],
    [48.028455187972774, 1.5507433232034882, 209.53492729681835],
    [53.35125605180922, 1.6352119585004592, 209.53474925909882],
    [58.80155160494701, 1.7172056265103606, 209.53457147176655],
    [64.37210171522501, 1.7969451471063824, 209.5343939420231],
    [70.05645182832635, 1.8746175094579132, 209.53421667601953],
    [75.8488028092011, 1.95038286970608, 209.53403967901312],
    [81.74390888832978, 2.0243797747220165, 209.53386295555885],
    [87.73699639870503, 2.0967291349022923, 209.53368650960735],
    [93.82369818202439, 2.1675372954936383, 209.53351034459058],
    [100.0, 2.2368984457707195, 209.5333344635329],
    [106.26219627903436, 2.304896533525034, 209.53315886906827],
    [112.60685320678104, 2.3716068043005607, 209.5329835635155],
    [119.03077768851209, 2.437097052049621, 209.53280854892182],
    [125.53099102420309, 2.501428645093027, 209.53263382708093],
    [132.1047064258276, 2.5646573751376196, 209.532459399577],
    [138.74930968646495, 2.6268341655120837, 209.53228526779512],
    [145.46234245739691, 2.688005666324115, 209.5321114329661],
    [152.24148769946316, 2.748214758003532, 209.5319378961533],
    [159.08455695969053, 2.807500980008346, 209.53176465830455],
    [165.98947919010237, 2.865900897958051, 209.53159172021918],
    [172.95429087732893, 2.92344841973748, 209.53141908260915],
    [179.97712729256875, 2.980175069050156, 209.531246746073],
    [187.05621470411134, 3.0361102232687336, 209.5310747111302],
    [194.18986342088985, 3.0912813211607015, 209.53090297820907],
    [201.3764615567875, 3.145714045061113, 209.5307315476577],
    [208.6144694227416, 3.199432481261756, 209.53056041976922],
    [215.90241446789472, 3.252459261745779, 209.5303895947692],
    [223.23888670275272, 3.3048156898733514, 209.53021907281337],
    [230.62253454702386, 3.356521852200883, 209.53004885402044],
    [238.05206105290918, 3.4075967182797573, 209.52987893845008],
    [245.52622046139462, 3.4580582299851543, 209.52970932613027],
    [253.04381505480674, 3.5079233817057034, 209.52954001701477],
    [260.6036922737095, 3.5572082925096393, 209.52937101105175],
    [268.20474207032214, 3.605928271271525, 209.52920230813686],
    [275.8458944741247, 3.654097875574637, 209.52903390813748],
    [283.52611734829725, 3.7017309651178785, 209.52886581088453],
    [291.24441431821003, 3.748840750239339, 209.52869801618866],
    [298.9998228553806, 3.795439836103318, 209.52853052381926],
    [306.7914125022303, 3.841540263013781, 209.52836333353144],
    [314.61828322461554, 3.8871535432700086, 209.52819644505487],
    [322.479563880563, 3.9322906949207233, 209.52802985809194],
    [330.37441079487513, 3.9769622727358533, 209.5278635723298],
    [338.30200643038665, 4.021178396670985, 209.52769758743247],
    [346.2615581476034, 4.064948778071929, 209.52753190304955],
    [354.2522970453064, 4.108282743840222, 209.52736651881136],
    [362.2734768754491, 4.151189258746347, 209.52720143432805],
    [370.32437302633326, 4.1936769460683285, 209.52703664919864],
    [378.40428156863675, 4.235754106704258, 209.52687216301322],
    [386.51251835937717, 4.277428736903083, 209.5267079753345],
    [394.648418199364, 4.3187085447228295, 209.52654408572644],
    [402.8113340400954, 4.359600965341976, 209.52638049373465],
    [411.00063623642933, 4.400113175309799, 209.52621719889768],
    [419.2157118416773, 4.440252105831943, 209.52605420073294],
    [427.45596394207547, 4.480024455165198, 209.52589149876238],
    [435.7208110278373, 4.519436700202084, 209.52572909248678],
    [444.00968639824373, 4.558495107300929, 209.52556698141063],
    [452.32203759843054, 4.597205742430248, 209.5254051650081],
    [460.65732588572826, 4.635574480668458, 209.52524364277477],
    [469.01502572358646, 4.67360701512636, 209.52508241417655],
    [477.39462430127537, 4.711308865316018, 209.52492147868517],
    [485.79562107768834, 4.7486853850221635, 209.5247608357571],
    [494.2175273477133, 4.7857417697075455, 209.52460048484275],
    [502.65986582975273, 4.822483063478878, 209.52444042540557],
    [511.12217027307815, 4.858914165665327, 209.52428065686505],
    [519.603985083808, 4.895039837005332, 209.52412117867837],
    [528.1048649683817, 4.9308647055023425, 209.52396199027322],
    [536.6243745934894, 4.966393271948785, 209.52380309107085],
    [545.162088261489, 5.001629915149562, 209.52364448049883],
    [553.7175896004151, 5.036578896863699, 209.52348615798226],
    [562.2904712677357, 5.071244366487241, 209.52332812293528],
    [570.8803346670916, 5.105630365484719, 209.52317037476547],
    [579.4867896772784, 5.139740831594337, 209.5230129128839],
    [588.1094543928114, 5.173579602816207, 209.52285573670093],
    [596.7479548754266, 5.20715042120039, 209.5226988456209],
    [605.4019249159434, 5.240456936444621, 209.52254223903395],
    [614.0710058059254, 5.273502709313967, 209.5223859163477],
    [622.7548461186354, 5.306291214893902, 209.52222987695998],
    [631.4531014987923, 5.338825845688801, 209.52207412025294],
    [640.1654344606808, 5.371109914568736, 209.52191864562857],
    [648.8915141941957, 5.403146657580354, 209.52176345246957],
    [657.6310163784137, 5.434939236625218, 209.52160854017026],
    [666.3836230023238, 5.466490742017985, 209.52145390810907],
    [675.1490221923619, 5.497804194921783, 209.5212995556808],
    [683.9269080464271, 5.528882549682189, 209.52114548225762],
    [692.7169804740557, 5.559728696047723, 209.52099168723132],
    [701.5189450424705, 5.590345461302892, 209.5208381699748],
    [710.3325128282281, 5.620735612298761, 209.52068492987144],
    [719.1574002741951, 5.6509018574012, 209.52053196630135],
    [727.9933290516212, 5.680846848355491, 209.52037927864566],
    [736.8400259270661, 5.710573182071791, 209.52022686627365],
    [745.6972226339658, 5.74008340233323, 209.5200747285655],
    [754.5646557486314, 5.769380001437249, 209.51992286490193],
    [763.4420665704857, 5.79846542176912, 209.51977127465065],
    [772.3292010063437, 5.827342057308235, 209.519619957194]]  # type: list[Vector]


class Achromatic(_Achromatic):
    """
    Test if color is achromatic.

    Should work quite well through the SDR range. Can reasonably handle HDR range out to 3
    which is far enough for anything practical.
    We use a spline mainly to quickly fit the line in a way we do not have to analyze and tune.
    """

    L_IDX = 0
    C_IDX = 1
    H_IDX = 2

    def __init__(
        self,
        data: list[Vector] | None = None,
        threshold_upper: float = 0.0,
        threshold_lower: float = 0.0,
        threshold_cutoff: float = float('inf'),
        spline: str = 'linear',
        mirror: bool = False,
        *,
        env: Environment,
        **kwargs: Any
    ) -> None:
        """Initialize."""

        super().__init__(data, threshold_upper, threshold_lower, threshold_cutoff, spline, mirror, env=env, **kwargs)

    def calc_achromatic_response(  # type: ignore[override]
        self,
        parameters: list[tuple[int, int, int, float]],
        *,
        env: Environment,
        **kwargs: Any
    ) -> None:  # pragma: no cover
        """Precalculate the achromatic response."""

        super().calc_achromatic_response(parameters, env=env, **kwargs)

    def convert(self, coords: Vector, *, env: Environment, **kwargs: Any) -> Vector:  # type: ignore[override]
        """Convert to the target color space."""

        return xyz_d65_to_cam16_jmh(lin_srgb_to_xyz(lin_srgb(coords)), env)


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
    constant = 100 / fl * (27.13 ** ADAPTED_COEF_INV)
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
        rgb_w = alg.dot(M16, xyz_w, dims=alg.D2_D1)

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
    # Unfortunately, `mypy` is not smart enough to tell which one is not `None`,
    # so we have to we must test each again later, but it is still faster than calling `cast()`.
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

    # Calculate hue from red-green and yellow-blue components
    a = rgb_a[0] + (-12 * rgb_a[1] + rgb_a[2]) / 11
    b = (rgb_a[0] + rgb_a[1] - 2 * rgb_a[2]) / 9
    h_rad = math.atan2(b, a) % alg.TAU

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
    J, M, h = cam16[0], cam16[5], cam16[2]
    return [max(0.0, J), max(0.0, M), h]


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
    # Assuming sRGB which has a lux of 64
    ENV = Environment(WHITE, 64 / math.pi * 0.2, 20, 'average', False)
    # If discounting were True, we could remove the dynamic achromatic response
    ACHROMATIC = Achromatic(
        # Precalculated from:
        # [
        #     (1, 5, 1, 1000.0),
        #     (1, 10, 1, 200.0),
        #     (5, 521, 5, 100.0)
        # ],
        ACHROMATIC_RESPONSE,
        0.0012,
        0.0141,
        6.7,
        'catrom',
        env=ENV
    )
    CHANNELS = (
        Channel("j", 0.0, 100.0, limit=(0.0, None)),
        Channel("m", 0, 105.0, limit=(0.0, None)),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE, nans=ACHROMATIC.hue)
    )

    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resolve channels."""

        if index == 2:
            h = coords[2]
            return self.ACHROMATIC.get_ideal_hue(coords[0]) if math.isnan(h) else h

        elif index == 1:
            c = coords[1]
            return self.ACHROMATIC.get_ideal_chroma(coords[0]) if math.isnan(c) else c

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return coords[0] == 0.0 or self.ACHROMATIC.test(coords[0], coords[1], coords[2])

    def to_base(self, coords: Vector) -> Vector:
        """From CAM16 JMh to XYZ."""

        return cam16_jmh_to_xyz_d65(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16 JMh."""

        return xyz_d65_to_cam16_jmh(coords, self.ENV)
