"""
Convert a temperature in Kelvin to a color.

Colors fall on the black body curve.
https://en.wikipedia.org/wiki/Planckian_locus
"""
from __future__ import annotations
import math
from . import algebra as alg
from . import util
from .cat import WHITES
from . import cmfs
from .types import VectorLike, Vector
from typing import Callable

# Constants for Planck's Law
H = 6.62607015e-34 * 1e18  # Plank's constant: `nm2 kg / s`
C = 299792458 * 1e9  # Speed of light: `nm / s`
K = 1.380649e-23 * 1e18  # Boltzmann constant: `nm2 kg s-2 K-1`
C1 = 2 * math.pi * H * C ** 2  # First radiation constant
C2 = (H * C) / K  # Second radiation constant

# Table for Robertson 1968 method
# Data: reciprocal temperature, u, v, slope
RUVT = [
    (0.0, 0.18006, 0.26352, -0.24341),
    (10.0, 0.18066, 0.26589, -0.25479),
    (20.0, 0.18133, 0.26846, -0.26876),
    (30.0, 0.18208, 0.27119, -0.28539),
    (40.0, 0.18293, 0.27407, -0.30470),
    (50.0, 0.18388, 0.27709, -0.32675),
    (60.0, 0.18494, 0.28021, -0.35156),
    (70.0, 0.18611, 0.28342, -0.37915),
    (80.0, 0.18740, 0.28668, -0.40955),
    (90.0, 0.18880, 0.28997, -0.44278),
    (100.0, 0.19032, 0.29326, -0.47888),
    (125.0, 0.19462, 0.30141, -0.58204),
    (150.0, 0.19962, 0.30921, -0.70471),
    (175.0, 0.20525, 0.31647, -0.84901),
    (200.0, 0.21142, 0.32312, -1.0182),
    (225.0, 0.21807, 0.32909, -1.2168),
    (250.0, 0.22511, 0.33439, -1.4512),
    (275.0, 0.23247, 0.33904, -1.7298),
    (300.0, 0.24010, 0.34308, -2.0637),
    (325.0, 0.24792, 0.34655, -2.4681),  # Note: 0.24792 is a corrected value for the error found in W&S as 0.24702
    (350.0, 0.25591, 0.34951, -2.9641),
    (375.0, 0.26400, 0.35200, -3.5814),
    (400.0, 0.27218, 0.35407, -4.3633),
    (425.0, 0.28039, 0.35577, -5.3762),
    (450.0, 0.28863, 0.35714, -6.7262),
    (475.0, 0.29685, 0.35823, -8.5955),
    (500.0, 0.30505, 0.35907, -11.324),
    (525.0, 0.31320, 0.35968, -15.628),
    (550.0, 0.32129, 0.36011, -23.325),
    (575.0, 0.32931, 0.36038, -40.770),
    (600.0, 0.33724, 0.36051, -116.45),
]

DEFAULT_WHITE = tuple(util.xy_to_xyz(WHITES['2deg']['D65']))


def temp_to_uv_planckian_locus(
    temp: float,
    cmf: dict[int, tuple[float, float, float]] = cmfs.cie_2_deg_observer,
    white: VectorLike = DEFAULT_WHITE,
    start: int = 360,
    end: int = 830,
    step: int = 5
) -> Vector:
    """
    Temperature to Planckian locus.

    https://en.wikipedia.org/wiki/Planckian_locus#The_Planckian_locus_in_the_XYZ_color_space
    """
    x = y = z = 0.0

    for wavelength in range(start, end + 1, step):
        m = C1 * (wavelength ** -5) * (math.exp(C2 / (wavelength * temp)) - 1.0) ** -1
        x += m * cmf[wavelength][0]
        y += m * cmf[wavelength][1]
        z += m * cmf[wavelength][2]

    xy = util.xyz_to_xyY([x, y, z], white)[:2]
    return util.xy_to_uv_1960(xy)


class BlackBodyCurve:
    """
    Setup a spline that represents the black body curve.

    Points between steps are approximated, but actual points can always be
    acquired via `exact`.
    """

    def __init__(
        self,
        cmf: dict[int, tuple[float, float, float]] = cmfs.cie_2_deg_observer,
        white: VectorLike = DEFAULT_WHITE
    ) -> None:
        """Initialize."""

        keys = list(cmf.keys())
        self.cmf_start = min(keys)
        self.cmf_end = max(keys)

        points = []
        self.domain = []
        self.domain2 = []
        self.cmf = cmf
        self.white = white
        start = 1000
        end = 20000
        step = 130
        inc = (end - start) / step
        count = step + 1

        for r in range(count):
            k = r * inc + start
            u, v = temp_to_uv_planckian_locus(k, self.cmf, self.white, self.cmf_start, self.cmf_end)
            self.domain.append(k)
            points.append([u, v])

        self.spline = alg.interpolate(points, method='monotone')

        start = end
        end = 100000
        step = 220
        inc = (end - start) / step
        count = step + 1
        points = []

        for r in range(count):
            k = r * inc + start
            u, v = temp_to_uv_planckian_locus(k, self.cmf, self.white, self.cmf_start, self.cmf_end)
            self.domain2.append(k)
            points.append([u, v])

        self.spline2 = alg.interpolate(points, method='monotone')

    def scale(self, point: float, domain: list[float]) -> float:
        """Scale the temperature point to match the range 0 - 1."""

        # Extrapolation
        if point <= domain[0]:
            point = (point - domain[0]) / (domain[-1] - domain[0])
        elif point >= self.domain[-1]:
            point = 1.0 + (point - domain[-1]) / (domain[-1] - domain[0])

        # Interpolation
        else:
            a, b = domain[0], domain[len(domain) - 1]
            l = b - a
            point = ((point - a) / l) if l else 0.0
        return point

    def __call__(self, temp: float, exact: bool = False) -> Vector:
        """Get the uv for the given temp."""

        if exact:
            return temp_to_uv_planckian_locus(temp, self.cmf, self.white, self.cmf_start, self.cmf_end)
        else:
            if temp <= 20000:
                return self.spline(self.scale(temp, self.domain))
            return self.spline2(self.scale(temp, self.domain2))


DEFAULT_BLACK_BODY = BlackBodyCurve()


def temp_to_uv_ohno_2013(
    temp: float,
    duv: float = 0.0,
    blackbody: BlackBodyCurve = DEFAULT_BLACK_BODY
) -> Vector:
    """
    Return uv given a temperature and Duv.

    If a Duv is given, a very small difference in temperature along the locus
    is calculated alongside the target. Then we can calculate the slope angle
    and apply the Duv.

    https://www.researchgate.net/publication/263373260_Practical_Use_and_Calculation_of_CCT_and_Duv
    """

    u0, v0 = blackbody(temp, exact=True)
    if duv:
        u1, v1 = blackbody(temp + 0.01, exact=True)
        du = u0 - u1
        dv = v0 - v1
        di = math.sqrt(du ** 2 + dv ** 2)
        if di:
            du /= di
            dv /= di
            u0 = u0 - duv * dv
            v0 = v0 + duv * du
    return [u0, v0]


def uv_to_temp_ohno_2013(
    uv: VectorLike,
    start: float = 1000,
    end: float = 100000,
    samples: int = 10,
    iterations: int = 6,
    exact: bool = False,
    blackbody: BlackBodyCurve = DEFAULT_BLACK_BODY
) -> Vector:
    """
    Calculate temperature for a given pair of uv coordinates.

    The Ohno approach requires a pre-generated table. The more data available, the more precise the values.
    Unfortunately, to span the entire range of 1000 - 100000 with fairly good accuracy, it requires keeping
    a very large table in memory.

    To avoid storing a large amount of data in memory, we can use multiple iterations and dynamically sample
    points on the locus, each iteration shrinking the bounds until we converge. Unfortunately, this is very
    slow, millisecond range.

    An alternative is to use the iterative approach, but generate a smaller subset of data and use a spline
    to approximate the points in between. Obviously, the points in between will not be as accurate, but the
    spline is used only as a way to approximate close to the temperature. Once we've sufficiently narrowed
    the range down to our best 3 temperature points, we can calculate those points with higher accuracy and
    proceed with the solvers. This actually allows us to use an even smaller amount of data than if we had
    used no spline and pre-calculated enough points for a similar accuracy. This is also much faster than
    dynamically calculating all the points.

    After navigating the table of data and determining a temperature that has the lowest delta distance, we can
    then use the triangular and parabolic solver. The triangular works best for values close to the locus (less
    than |0.002| Duv) and the parabolic solution works better for values with a higher Duv.

    For more precision, `exact` will avoid the approximation spline.

    https://www.researchgate.net/publication/263373260_Practical_Use_and_Calculation_of_CCT_and_Duv
    """

    u, v = uv
    last = samples - 1
    index = 0
    table = []  # type: list[tuple[float, float, float, float]]

    # Each iteration we narrow the range until we are close enough
    for _ in range(iterations):
        table.clear()
        lowest = alg.INF
        index = 0

        # Generate the Planckian table while tracking lowest distance
        for j in range(samples):
            k = alg.lerp(start, end, j / last)
            u2, v2 = blackbody(k, exact=exact)
            di = math.sqrt((u2 - u) ** 2 + (v2 - v) ** 2)
            if di < lowest:
                lowest = di
                index = j
            table.append((k, u2, v2, di))

        # Set next iteration's range to include our best result +/-1
        # If our best result was on the edge, that edge remains the boundary
        start = table[index - 1][0] if index > 0 else table[index][0]
        end = table[index + 1][0] if index < last else table[index][0]

    # Select the closest 3 values. Get precise values instead of our
    # approximated spline value so we can get the most accurate result.
    ti = table[index][0]
    if not exact:
        ui, vi = blackbody(ti, exact=True)
        di = math.sqrt((ui - u) ** 2 + (vi - v) ** 2)
    else:
        di = table[index][-1]

    if index == 0 or not exact:
        tp = ti - 1e-4 if index == 0 else table[index - 1][0]
        up, vp = blackbody(tp, exact=True)
        dp = math.sqrt((up - u) ** 2 + (vp - v) ** 2)
    else:
        tp, up, vp, dp = table[index - 1]

    if index == last or not exact:
        tn = ti + 1e-4 if index == last else table[index + 1][0]
        un, vn = blackbody(tn, exact=True)
        dn = math.sqrt((un - u) ** 2 + (vn - v) ** 2)
    else:
        tn, un, vn, dn = table[index + 1]

    # Triangular solution
    l = math.sqrt((un - up) ** 2 + (vn - vp) ** 2)
    x = (dp ** 2 - dn ** 2 + l ** 2) / (2 * l)
    t = tp + (tn - tp) * (x / l)
    vtx = vp + (vn - vp) * (x / l)
    sign = math.copysign(1, v - vtx)
    duv = (dp ** 2 - x ** 2) ** (1 / 2) * sign

    # Parabolic solution
    if abs(duv) >= 0.002:
        x = (tn - ti) * (tp - tn) * (ti - tp)
        a = (
            tp * (dn - di) +
            ti * (dp - dn) +
            tn * (di - dp)
        ) * (x ** -1)
        b = -(
            (tp ** 2) * (dn - di) +
            (ti ** 2) * (dp - dn) +
            (tn ** 2) * (di - dp)
        ) * (x ** -1)
        c = -(
            (dp * ti * tn) * (tn - ti) +
            (di * tp * tn) * (tp - tn) +
            (dn * tp * ti) * (ti - tp)
        ) * (x ** -1)
        t = -b / (2 * a)
        duv = (a * (t ** 2) + b * t + c) * sign

    return [t, duv]


def uv_to_temp_robertson_1968(uv: VectorLike) -> Vector:
    """
    Calculate temperature from uv coordinates.

    Uses Robertson 1968 method.
    - https://en.wikipedia.org/wiki/Correlated_color_temperature#Robertson's_method
    - http://www.brucelindbloom.com/index.html?Math.html

    Distance between test point and the point on the locus is given by:

    ```
    di = ((vt - vi) - mt * (ut - ui)) / (1 + mt ** 2) ** (1/2)
    ```

    We need to find the two isotherms where the given uv is between.
    Once found, we simply need to interpolate the temperature between them.

    The Duv can be found by calculating the distance between the point
    on the locus and our given point. Then slope vector between the isotherms
    can be calculated and used to determine the offset.
    """

    # Search for line pair coordinate is between.
    previous_di = temp = duv = 0.0
    u, v = uv
    end = len(RUVT) - 1

    for index, current in enumerate(RUVT):
        # Get the distance
        di = (v - current[2]) - current[3] * (u - current[1])
        if index > 0 and (di <= 0.0 or index == end):
            # Calculate the required interpolation factor between the two lines
            previous = RUVT[index - 1]
            current_denom = math.sqrt(1.0 + current[3] ** 2)
            di /= current_denom
            previous_denom = math.sqrt(1.0 + previous[3] ** 2)
            dip = previous_di / previous_denom
            factor = dip / (dip - di)

            # Calculate the temperature, if the mired value is zero
            # assume the maximum temperature of 100000K.
            mired = alg.lerp(previous[0], current[0], factor)
            temp = 1.0E6 / mired if mired > 0 else 1e5

            # Interpolate the slope vectors
            dup = 1 / previous_denom
            dvp = previous[3] / previous_denom
            du = 1 / current_denom
            dv = current[3] / current_denom
            du = alg.lerp(dup, du, factor)
            dv = alg.lerp(dvp, dv, factor)
            denom = math.sqrt(du ** 2 + dv ** 2)
            du /= denom
            dv /= denom

            # Calculate Duv
            duv = (
                du * (u - alg.lerp(previous[1], current[1], factor)) +
                dv * (v - alg.lerp(previous[2], current[2], factor))
            )

            break

        # Save distance as previous
        previous_di = di

    return [temp, -duv]


def temp_to_uv_robertson_1968(cct: float, duv: float = 0.0) -> Vector:
    """
    Temperature to uv coordinates.

    Uses Robertson 1968 method.
    - https://en.wikipedia.org/wiki/Correlated_color_temperature#Robertson's_method
    - http://www.brucelindbloom.com/index.html?Math.html
    """

    # Find inverse temperature to use as index.
    r = 1.0E6 / cct
    u = v = 0.0
    end = len(RUVT) - 2

    for index, current in enumerate(RUVT):
        future = RUVT[index + 1]

        # Find the two isotherms that our target temp is between
        if r < future[0] or index == end:
            # Find relative weight between the two values
            f = (future[0] - r) / (future[0] - current[0])

            # Interpolate the uv coordinates of our target temperature
            u = alg.lerp(future[1], current[1], f)
            v = alg.lerp(future[2], current[2], f)

            # Calculate the offset along the slope
            if duv:
                # Calculate the slope vectors
                u1 = 1.0
                v1 = current[3]
                length = math.sqrt(1.0 + v1 ** 2)
                u1 /= length
                v1 /= length

                u2 = 1.0
                v2 = future[3]
                length = math.sqrt(1.0 + v2 ** 2)
                u2 /= length
                v2 /= length

                # Find vector from the locus to our point.
                du = alg.lerp(u2, u1, f)
                dv = alg.lerp(v2, v1, f)
                denom = math.sqrt(du ** 2 + dv ** 2)
                du /= denom
                dv /= denom

                # Adjust the uv by the calculated offset
                u += du * -duv
                v += dv * -duv
            break

    return [u, v]


SUPPORTED_TO = {
    'ohno-2013': uv_to_temp_ohno_2013,
    'robertson-1968': uv_to_temp_robertson_1968,
}  # type: dict[str, Callable[..., Vector]]

SUPPORTED_FROM = {
    'ohno-2013': temp_to_uv_ohno_2013,
    'robertson-1968': temp_to_uv_robertson_1968,
}  # type: dict[str, Callable[..., Vector]]


def to_cct(name: str) -> Callable[..., Vector]:
    """Get the method for calculating to CCT."""

    cct = SUPPORTED_TO.get(name)
    if not cct:
        raise ValueError("The CCT algorithm '{}' cannot be found".format(name))
    return cct


def from_cct(name: str) -> Callable[..., Vector]:
    """Get the method for calculating from CCT."""

    cct = SUPPORTED_FROM.get(name)
    if not cct:
        raise ValueError("The CCT algorithm '{}' cannot be found".format(name))
    return cct
