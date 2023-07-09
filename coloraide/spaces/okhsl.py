"""
Okhsl class.

Adapted to ColorAide Python and ColorAide by Isaac Muse (2021)

---- License ----

Copyright (c) 2021 Björn Ottosson

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations
from .hsl import HSL
from ..channels import Channel, FLG_ANGLE
from .. import util
import math
import sys
from .. import algebra as alg
from ..types import Vector, Matrix
from . oklab import OKLAB_TO_LMS3

SRGBL_TO_LMS = [
    [0.41222146947076277, 0.536332537261735, 0.051445993267502196],
    [0.21190349581782508, 0.6806995506452346, 0.10739695353694051],
    [0.08830245919005636, 0.2817188391361215, 0.6299787016738223]
]

LMS_TO_SRGBL = [
    [4.07674163607596, -3.3077115392580643, 0.23096990318210434],
    [-1.268437973285031, 2.6097573492876878, -0.3413193760026569],
    [-0.004196076138675668, -0.7034186179359357, 1.707614694074611]
]

SRGBL_COEFF = [
    # Red
    [
        # Limit
        [-1.8817031, -0.80936501],
        # `Kn` coefficients
        [1.19086277, 1.76576728, 0.59662641, 0.75515197, 0.56771245]
    ],
    # Green
    [
        # Limit
        [1.8144408, -1.19445267],
        # `Kn` coefficients
        [0.73956515, -0.45954404, 0.08285427, 0.12541073, -0.14503204]
    ],
    # Blue
    [
        # Limit
        [0.13110758, 1.81333971],
        # `Kn` coefficients
        [1.35691337, -0.00927067, -1.15076778, -0.50647483, 0.00645602]
    ]
]  # type: list[list[Vector]]

FLT_MAX = sys.float_info.max

K_1 = 0.206
K_2 = 0.03
K_3 = (1.0 + K_1) / (1.0 + K_2)


def toe(x: float) -> float:
    """Toe function for L_r."""

    return 0.5 * (K_3 * x - K_1 + math.sqrt((K_3 * x - K_1) * (K_3 * x - K_1) + 4 * K_2 * K_3 * x))


def toe_inv(x: float) -> float:
    """Inverse toe function for L_r."""

    return (x ** 2 + K_1 * x) / (K_3 * (x + K_2))


def to_st(cusp: Vector) -> Vector:
    """To ST."""

    l, c = cusp
    return [c / l, c / (1 - l)]


def get_st_mid(a: float, b: float) -> Vector:
    """
    Returns a smooth approximation of the location of the cusp.

    This polynomial was created by an optimization process.
    It has been designed so that S_mid < S_max and T_mid < T_max.
    """

    s = 0.11516993 + 1.0 / (
        7.44778970 + 4.15901240 * b +
        a * (
            -2.19557347 + 1.75198401 * b +
            a * (
                -2.13704948 - 10.02301043 * b +
                a * (
                    -4.24894561 + 5.38770819 * b + 4.69891013 * a
                )
            )
        )
    )

    t = 0.11239642 + 1.0 / (
        1.61320320 - 0.68124379 * b +
        a * (
            0.40370612 + 0.90148123 * b +
            a * (
                -0.27087943 + 0.61223990 * b +
                a * (
                    0.00299215 - 0.45399568 * b - 0.14661872 * a
                )
            )
        )
    )

    return [s, t]


def oklab_to_linear_rgb(lab: Vector, lms_to_rgb: Matrix) -> Vector:
    """
    Convert from Oklab to linear RGB.

    Can be any gamut as long as `lms_to_rgb` is a matrix
    that transform the LMS values to the linear RGB space.
    """

    return alg.dot(
        lms_to_rgb,
        [c ** 3 for c in alg.dot(OKLAB_TO_LMS3, lab, dims=alg.D2_D1)],
        dims=alg.D2_D1
    )


def find_cusp(
    a: float,
    b: float,
    lms_to_rgb: Matrix,
    ok_coeff: list[list[Vector]]
) -> Vector:
    """
    Finds L_cusp and C_cusp for a given hue.

    `a` and `b` must be normalized so `a^2 + b^2 == 1`.
    """

    # First, find the maximum saturation (saturation `S = C/L`)
    s_cusp = compute_max_saturation(a, b, lms_to_rgb, ok_coeff)

    # Convert to linear RGB to find the first point where at least one of r, g or b >= 1:
    r, g, b = oklab_to_linear_rgb([1, s_cusp * a, s_cusp * b], lms_to_rgb)
    l_cusp = alg.nth_root(1.0 / max(max(r, g), b), 3)
    c_cusp = l_cusp * s_cusp

    return [l_cusp, c_cusp]


def find_gamut_intersection(
    a: float,
    b: float,
    l1: float,
    c1: float,
    l0: float,
    lms_to_rgb: Matrix,
    ok_coeff: list[list[Vector]],
    cusp: Vector | None = None,
) -> float:
    """
    Finds intersection of the line.

    Defined by the following:

    ```
    L = L0 * (1 - t) + t * L1
    C = t * C1
    ```

    `a` and `b` must be normalized so `a^2 + b^2 == 1`.
    """

    if cusp is None:  # pragma: no cover
        cusp = find_cusp(a, b, lms_to_rgb, ok_coeff)

    # Find the intersection for upper and lower half separately
    if ((l1 - l0) * cusp[1] - (cusp[0] - l0) * c1) <= 0.0:
        # Lower half
        t = cusp[1] * l0 / (c1 * cusp[0] + cusp[1] * (l0 - l1))
    else:
        # Upper half

        # First intersect with triangle
        t = cusp[1] * (l0 - 1.0) / (c1 * (cusp[0] - 1.0) + cusp[1] * (l0 - l1))

        # Then one step Halley's method
        dl = l1 - l0
        dc = c1

        k_l = alg.vdot(OKLAB_TO_LMS3[0][1:], [a, b])
        k_m = alg.vdot(OKLAB_TO_LMS3[1][1:], [a, b])
        k_s = alg.vdot(OKLAB_TO_LMS3[2][1:], [a, b])

        l_dt = dl + dc * k_l
        m_dt = dl + dc * k_m
        s_dt = dl + dc * k_s

        # If higher accuracy is required, 2 or 3 iterations of the following block can be used:
        L = l0 * (1.0 - t) + t * l1
        C = t * c1

        l_ = L + C * k_l
        m_ = L + C * k_m
        s_ = L + C * k_s

        l = l_ ** 3
        m = m_ ** 3
        s = s_ ** 3

        ldt = 3 * l_dt * (l_ ** 2)
        mdt = 3 * m_dt * (m_ ** 2)
        sdt = 3 * s_dt * (s_ ** 2)

        ldt2 = 6 * (l_dt ** 2) * l_
        mdt2 = 6 * (m_dt ** 2) * m_
        sdt2 = 6 * (s_dt ** 2) * s_

        r = alg.vdot(lms_to_rgb[0], [l, m, s]) - 1
        r1 = alg.vdot(lms_to_rgb[0], [ldt, mdt, sdt])
        r2 = alg.vdot(lms_to_rgb[0], [ldt2, mdt2, sdt2])

        u_r = r1 / (r1 * r1 - 0.5 * r * r2)
        t_r = -r * u_r

        g = alg.vdot(lms_to_rgb[1], [l, m, s]) - 1
        g1 = alg.vdot(lms_to_rgb[1], [ldt, mdt, sdt])
        g2 = alg.vdot(lms_to_rgb[1], [ldt2, mdt2, sdt2])

        u_g = g1 / (g1 * g1 - 0.5 * g * g2)
        t_g = -g * u_g

        b = alg.vdot(lms_to_rgb[2], [l, m, s]) - 1
        b1 = alg.vdot(lms_to_rgb[2], [ldt, mdt, sdt])
        b2 = alg.vdot(lms_to_rgb[2], [ldt2, mdt2, sdt2])

        u_b = b1 / (b1 * b1 - 0.5 * b * b2)
        t_b = -b * u_b

        t_r = t_r if u_r >= 0.0 else FLT_MAX
        t_g = t_g if u_g >= 0.0 else FLT_MAX
        t_b = t_b if u_b >= 0.0 else FLT_MAX

        t += min(t_r, min(t_g, t_b))

    return t


def get_cs(
    lab: Vector,
    lms_to_rgb: Matrix,
    ok_coeff: list[list[Vector]]
) -> Vector:
    """Get Cs."""

    l, a, b = lab

    cusp = find_cusp(a, b, lms_to_rgb, ok_coeff)

    c_max = find_gamut_intersection(a, b, l, 1, l, lms_to_rgb, ok_coeff, cusp)
    st_max = to_st(cusp)

    # Scale factor to compensate for the curved part of gamut shape:
    k = c_max / min((l * st_max[0]), (1 - l) * st_max[1])

    st_mid = get_st_mid(a, b)

    # Use a soft minimum function, instead of a sharp triangle shape to get a smooth value for chroma.
    c_a = l * st_mid[0]
    c_b = (1.0 - l) * st_mid[1]
    c_mid = 0.9 * k * math.sqrt(math.sqrt(1.0 / (1.0 / (c_a ** 4) + 1.0 / (c_b ** 4))))

    # For `C_0`, the shape is independent of hue, so `ST` are constant.
    # Values picked to roughly be the average values of `ST`.
    c_a = l * 0.4
    c_b = (1.0 - l) * 0.8

    # Use a soft minimum function, instead of a sharp triangle shape to get a smooth value for chroma.
    c_0 = math.sqrt(1.0 / (1.0 / (c_a ** 2) + 1.0 / (c_b ** 2)))

    return [c_0, c_mid, c_max]


def compute_max_saturation(
    a: float,
    b: float,
    lms_to_rgb: Matrix,
    ok_coeff: list[list[Vector]]
) -> float:
    """
    Finds the maximum saturation possible for a given hue that fits in RGB.

    Saturation here is defined as `S = C/L`.
    `a` and `b` must be normalized so `a^2 + b^2 == 1`.
    """

    # Max saturation will be when one of r, g or b goes below zero.

    # Select different coefficients depending on which component goes below zero first.

    if alg.vdot(ok_coeff[0][0], [a, b]) > 1:
        # Red component
        k0, k1, k2, k3, k4 = ok_coeff[0][1]
        wl, wm, ws = lms_to_rgb[0]

    elif alg.vdot(ok_coeff[1][0], [a, b]) > 1:
        # Green component
        k0, k1, k2, k3, k4 = ok_coeff[1][1]
        wl, wm, ws = lms_to_rgb[1]

    else:
        # Blue component
        k0, k1, k2, k3, k4 = ok_coeff[2][1]
        wl, wm, ws = lms_to_rgb[2]

    # Approximate max saturation using a polynomial:
    sat = k0 + k1 * a + k2 * b + k3 * (a ** 2) + k4 * a * b

    # Do one step Halley's method to get closer.
    # This gives an error less than 10e6, except for some blue hues where the `dS/dh` is close to infinite.
    # This should be sufficient for most applications, otherwise do two/three steps.

    k_l = alg.vdot(OKLAB_TO_LMS3[0][1:], [a, b])
    k_m = alg.vdot(OKLAB_TO_LMS3[1][1:], [a, b])
    k_s = alg.vdot(OKLAB_TO_LMS3[2][1:], [a, b])

    l_ = 1.0 + sat * k_l
    m_ = 1.0 + sat * k_m
    s_ = 1.0 + sat * k_s

    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3

    l_ds = 3.0 * k_l * (l_ ** 2)
    m_ds = 3.0 * k_m * (m_ ** 2)
    s_ds = 3.0 * k_s * (s_ ** 2)

    l_ds2 = 6.0 * (k_l ** 2) * l_
    m_ds2 = 6.0 * (k_m ** 2) * m_
    s_ds2 = 6.0 * (k_s ** 2) * s_

    f = wl * l + wm * m + ws * s
    f1 = wl * l_ds + wm * m_ds + ws * s_ds
    f2 = wl * l_ds2 + wm * m_ds2 + ws * s_ds2

    sat = sat - f * f1 / ((f1 ** 2) - 0.5 * f * f2)

    return sat


def okhsl_to_oklab(
    hsl: Vector,
    lms_to_rgb: Matrix,
    ok_coeff: list[list[Vector]]
) -> Vector:
    """Convert Okhsl to Oklab."""

    h, s, l = hsl
    h = h / 360.0

    L = toe_inv(l)
    a = b = 0.0

    if L != 0.0 and L != 1.0 and s != 0:
        a_ = math.cos(2.0 * math.pi * h)
        b_ = math.sin(2.0 * math.pi * h)

        c_0, c_mid, c_max = get_cs([L, a_, b_], lms_to_rgb, ok_coeff)

        # Interpolate the three values for C so that:
        # ```
        # At s=0: dC/ds = C_0, C=0
        # At s=0.8: C=C_mid
        # At s=1.0: C=C_max
        # ```

        mid = 0.8
        mid_inv = 1.25

        if s < mid:
            t = mid_inv * s
            k_0 = 0.0
            k_1 = mid * c_0
            k_2 = (1.0 - k_1 / c_mid)

        else:
            t = 5 * (s - 0.8)
            k_0 = c_mid
            k_1 = 0.2 * (c_mid ** 2) * (1.25 ** 2) / c_0
            k_2 = 1.0 - k_1 / (c_max - c_mid)

        c = k_0 + t * k_1 / (1.0 - k_2 * t)

        a = c * a_
        b = c * b_

    return [L, a, b]


def oklab_to_okhsl(
    lab: Vector,
    lms_to_rgb: Matrix,
    ok_coeff: list[list[Vector]]
) -> Vector:
    """Oklab to Okhsl."""

    L = lab[0]
    s = 0.0
    l = toe(L)

    c = math.sqrt(lab[1] ** 2 + lab[2] ** 2)
    h = 0.5 + 0.5 * math.atan2(-lab[2], -lab[1]) / math.pi

    if l != 0.0 and l != 1.0 and c != 0:
        a_ = lab[1] / c
        b_ = lab[2] / c

        c_0, c_mid, c_max = get_cs([L, a_, b_], lms_to_rgb, ok_coeff)

        mid = 0.8
        mid_inv = 1.25

        if (c < c_mid):
            k_1 = mid * c_0
            k_2 = 1.0 - k_1 / c_mid

            t = c / (k_1 + k_2 * c)
            s = t * mid

        else:
            k_0 = c_mid
            k_1 = 0.2 * (c_mid ** 2) * (mid_inv ** 2) / c_0
            k_2 = (1.0 - (k_1) / (c_max - c_mid))

            t = (c - k_0) / (k_1 + k_2 * (c - k_0))
            s = mid + 0.2 * t

    return [util.constrain_hue(h * 360), s, l]


class Okhsl(HSL):
    """HSL class."""

    BASE = "oklab"
    NAME = "okhsl"
    SERIALIZE = ("--okhsl",)
    CHANNELS = (
        Channel("h", 0.0, 360.0, bound=True, flags=FLG_ANGLE),
        Channel("s", 0.0, 1.0, bound=True),
        Channel("l", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "lightness": "l"
    }

    def to_base(self, coords: Vector) -> Vector:
        """To Oklab from Okhsl."""

        return okhsl_to_oklab(coords, LMS_TO_SRGBL, SRGBL_COEFF)

    def from_base(self, coords: Vector) -> Vector:
        """From Oklab to Okhsl."""

        return oklab_to_okhsl(coords, LMS_TO_SRGBL, SRGBL_COEFF)
