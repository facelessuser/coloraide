"""
Ohno 2013 CCT calculations.

https://www.researchgate.net/publication/263373260_Practical_Use_and_Calculation_of_CCT_and_Duv
"""
from __future__ import annotations
import math
from . import planck
from .. import cat
from .. import cmfs
from .. import util
from .. import algebra as alg
from ..temperature import CCT
from ..types import Vector, VectorLike
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class BlackBodyCurve:
    """
    Setup a spline that represents the black body curve.

    Points between steps are approximated, but actual points can always be
    acquired via `exact`.

    For improved accuracy, we split spline data for low temps and high temps
    and assign the number of required data points accordingly.
    """

    def __init__(
        self,
        cmfs: dict[int, tuple[float, float, float]] = cmfs.CIE_1931_2DEG,
        white: VectorLike = cat.WHITES['2deg']['D65'],
        planck_step: int = 5,
        chromaticity: str = 'uv-1960'
    ) -> None:
        """Initialize."""

        keys = list(cmfs.keys())
        self.cmfs_start = min(keys)
        self.cmfs_end = max(keys)
        self.cmfs = cmfs
        self.white = util.xy_to_xyz(white)
        self.planck_step = planck_step
        self.to_uv = util.xy_to_uv_1960 if chromaticity == 'uv-1960' else util.xy_to_uv

        # Low temperature range
        start = 1000
        end = 20000
        step = 130
        inc = (end - start) / step
        count = step + 1
        points = []
        self.domain = []
        for r in range(count):
            k = r * inc + start
            u, v = self.to_uv(
                planck.temp_to_xy_planckian_locus(
                    k, self.cmfs, self.white, self.cmfs_start, self.cmfs_end, self.planck_step
                )
            )
            self.domain.append(k)
            points.append([u, v])
        self.spline = alg.interpolate(points, method='catrom')

        # High temperature range
        start = end
        end = 100000
        step = 220
        inc = (end - start) / step
        count = step + 1
        points = []
        self.domain2 = []
        for r in range(count):
            k = r * inc + start
            u, v = self.to_uv(
                planck.temp_to_xy_planckian_locus(
                    k, self.cmfs, self.white, self.cmfs_start, self.cmfs_end, self.planck_step
                )
            )
            self.domain2.append(k)
            points.append([u, v])
        self.spline2 = alg.interpolate(points, method='catrom')

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
            return self.to_uv(
                planck.temp_to_xy_planckian_locus(
                    temp, self.cmfs, self.white, self.cmfs_start, self.cmfs_end, self.planck_step
                )
            )
        else:
            if temp <= 20000:
                return self.spline(self.scale(temp, self.domain))
            return self.spline2(self.scale(temp, self.domain2))


class Ohno2013(CCT):
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

    NAME = 'ohno-2013'
    CHROMATICITY = 'uv-1960'

    def __init__(
        self,
        cmfs: dict[int, tuple[float, float, float]] = cmfs.CIE_1931_2DEG,
        white: VectorLike = cat.WHITES['2deg']['D65'],
        planck_step: int = 5
    ):
        """Initialize."""

        self.white = white
        self.blackbody = BlackBodyCurve(cmfs, white, planck_step, self.CHROMATICITY)

    def to_cct(
        self,
        color: Color,
        start: float = 1000,
        end: float = 100000,
        samples: int = 10,
        iterations: int = 6,
        exact: bool = False,
        **kwargs: Any
    ) -> Vector:
        """Calculate a color's CCT."""

        u, v = color.split_chromaticity(self.CHROMATICITY)[:-1]
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
                u2, v2 = self.blackbody(k, exact=exact)
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
            ui, vi = self.blackbody(ti, exact=True)
            di = math.sqrt((ui - u) ** 2 + (vi - v) ** 2)
        else:
            di = table[index][-1]

        if index == 0 or not exact:
            tp = ti - 1e-4 if index == 0 else table[index - 1][0]
            up, vp = self.blackbody(tp, exact=True)
            dp = math.sqrt((up - u) ** 2 + (vp - v) ** 2)
        else:
            tp, up, vp, dp = table[index - 1]

        if index == last or not exact:
            tn = ti + 1e-4 if index == last else table[index + 1][0]
            un, vn = self.blackbody(tn, exact=True)
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

    def from_cct(
        self,
        color: type[Color],
        space: str,
        kelvin: float,
        duv: float,
        scale: bool,
        scale_space: str | None,
        **kwargs: Any
    ) -> Color:
        """Calculate a color that satisfies the CCT using Planck's law."""

        u0, v0 = self.blackbody(kelvin, exact=True)
        if duv:
            u1, v1 = self.blackbody(kelvin + 0.01, exact=True)
            du = u0 - u1
            dv = v0 - v1
            di = math.sqrt(du ** 2 + dv ** 2)
            if di:
                du /= di
                dv /= di
                u0 = u0 - duv * dv
                v0 = v0 + duv * du

        return color.chromaticity(space, [u0, v0, 1], self.CHROMATICITY, scale=scale, scale_space=scale_space)
