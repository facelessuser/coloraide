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
from ..spaces import Space, Cylindrical
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .oklab import oklab_to_linear_srgb
from .oklch import ACHROMATIC_THRESHOLD
from .. import util
import math
import sys
from .. import algebra as alg
from ..types import Vector
from typing import Optional

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


def find_cusp(a: float, b: float) -> Vector:
    """
    Finds L_cusp and C_cusp for a given hue.

    `a` and `b` must be normalized so `a^2 + b^2 == 1`.
    """

    # First, find the maximum saturation (saturation `S = C/L`)
    s_cusp = compute_max_saturation(a, b)

    # Convert to linear sRGB to find the first point where at least one of r, g or b >= 1:
    r, g, b = oklab_to_linear_srgb([1, s_cusp * a, s_cusp * b])
    l_cusp = alg.nth_root(1.0 / max(max(r, g), b), 3)
    c_cusp = l_cusp * s_cusp

    return [l_cusp, c_cusp]


def find_gamut_intersection(
    a: float,
    b: float,
    l1: float,
    c1: float,
    l0: float,
    cusp: Optional[Vector] = None
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
        cusp = find_cusp(a, b)

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

        k_l = +0.3963377774 * a + 0.2158037573 * b
        k_m = -0.1055613458 * a - 0.0638541728 * b
        k_s = -0.0894841775 * a - 1.2914855480 * b

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

        r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s - 1
        r1 = 4.0767416621 * ldt - 3.3077115913 * mdt + 0.2309699292 * sdt
        r2 = 4.0767416621 * ldt2 - 3.3077115913 * mdt2 + 0.2309699292 * sdt2

        u_r = r1 / (r1 * r1 - 0.5 * r * r2)
        t_r = -r * u_r

        g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s - 1
        g1 = -1.2684380046 * ldt + 2.6097574011 * mdt - 0.3413193965 * sdt
        g2 = -1.2684380046 * ldt2 + 2.6097574011 * mdt2 - 0.3413193965 * sdt2

        u_g = g1 / (g1 * g1 - 0.5 * g * g2)
        t_g = -g * u_g

        b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s - 1
        b1 = -0.0041960863 * ldt - 0.7034186147 * mdt + 1.7076147010 * sdt
        b2 = -0.0041960863 * ldt2 - 0.7034186147 * mdt2 + 1.7076147010 * sdt2

        u_b = b1 / (b1 * b1 - 0.5 * b * b2)
        t_b = -b * u_b

        t_r = t_r if u_r >= 0.0 else FLT_MAX
        t_g = t_g if u_g >= 0.0 else FLT_MAX
        t_b = t_b if u_b >= 0.0 else FLT_MAX

        t += min(t_r, min(t_g, t_b))

    return t


def get_cs(lab: Vector) -> Vector:
    """Get Cs."""

    l, a, b = lab

    cusp = find_cusp(a, b)

    c_max = find_gamut_intersection(a, b, l, 1, l, cusp)
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


def compute_max_saturation(a: float, b: float) -> float:
    """
    Finds the maximum saturation possible for a given hue that fits in sRGB.

    Saturation here is defined as `S = C/L`.
    `a` and `b` must be normalized so `a^2 + b^2 == 1`.
    """

    # Max saturation will be when one of r, g or b goes below zero.

    # Select different coefficients depending on which component goes below zero first.

    if (-1.88170328 * a - 0.80936493 * b) > 1:
        # Red component
        k0 = 1.19086277
        k1 = 1.76576728
        k2 = 0.59662641
        k3 = 0.75515197
        k4 = 0.56771245
        wl = 4.0767416621
        wm = -3.3077115913
        ws = 0.2309699292

    elif (1.81444104 * a - 1.19445276 * b) > 1:
        # Green component
        k0 = 0.73956515
        k1 = -0.45954404
        k2 = 0.08285427
        k3 = 0.12541070
        k4 = 0.14503204
        wl = -1.2684380046
        wm = 2.6097574011
        ws = -0.3413193965

    else:
        # Blue component
        k0 = 1.35733652
        k1 = -0.00915799
        k2 = -1.15130210
        k3 = -0.50559606
        k4 = 0.00692167
        wl = -0.0041960863
        wm = -0.7034186147
        ws = 1.7076147010

    # Approximate max saturation using a polynomial:
    sat = k0 + k1 * a + k2 * b + k3 * (a ** 2) + k4 * a * b

    # Do one step Halley's method to get closer.
    # This gives an error less than 10e6, except for some blue hues where the `dS/dh` is close to infinite.
    # This should be sufficient for most applications, otherwise do two/three steps.

    k_l = 0.3963377774 * a + 0.2158037573 * b
    k_m = -0.1055613458 * a - 0.0638541728 * b
    k_s = -0.0894841775 * a - 1.2914855480 * b

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


def okhsl_to_oklab(hsl: Vector) -> Vector:
    """Convert Okhsl to sRGB."""

    h, s, l = hsl
    h = h / 360.0

    L = toe_inv(l)
    a = b = 0.0

    if L != 0.0 and abs(1 - L) >= 1e-08 and abs(s) >= ACHROMATIC_THRESHOLD and not alg.is_nan(h):
        a_ = math.cos(2.0 * math.pi * h)
        b_ = math.sin(2.0 * math.pi * h)

        c_0, c_mid, c_max = get_cs([L, a_, b_])

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


def oklab_to_okhsl(lab: Vector) -> Vector:
    """Oklab to Okhsl."""

    h = alg.NaN
    L = lab[0]
    s = 0.0
    l = toe(L)

    c = math.sqrt(lab[1] ** 2 + lab[2] ** 2)
    if c < ACHROMATIC_THRESHOLD:
        c = 0.0

    if l != 0.0 and abs(1 - l) >= 1e-08 and c != 0:
        a_ = lab[1] / c
        b_ = lab[2] / c

        h = 0.5 + 0.5 * math.atan2(-lab[2], -lab[1]) / math.pi

        c_0, c_mid, c_max = get_cs([L, a_, b_])

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

    if abs(s) < ACHROMATIC_THRESHOLD:
        h = alg.NaN

    return [util.constrain_hue(h * 360), s, l]


class Okhsl(Cylindrical, Space):
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
    WHITE = WHITES['2deg']['D65']
    GAMUT_CHECK = "srgb"

    def normalize(self, coords: Vector) -> Vector:
        """On color update."""

        coords = alg.no_nans(coords)
        if coords[2] == 0.0 or abs(1 - coords[2]) < 1e-08 or abs(coords[1]) < ACHROMATIC_THRESHOLD:
            coords[0] = alg.NaN
        return coords

    def to_base(self, coords: Vector) -> Vector:
        """To Oklab from Okhsl."""

        return okhsl_to_oklab(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From Oklab to Okhsl."""

        return oklab_to_okhsl(coords)
