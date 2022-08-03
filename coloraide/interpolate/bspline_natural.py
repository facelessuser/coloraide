"""
Natural B-Spline interpolation.

https://www.math.ucla.edu/~baker/149.1.02w/handouts/dd_splines.pdf.
"""
from .. interpolate import Interpolate, Interpolator
from functools import lru_cache
from .bspline import InterpolatorBSpline
from coloraide import algebra as alg
from ..types import Vector, Matrix
from typing import List, Sequence, Any, Optional, Union, Mapping, Callable, Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

M141 = [1, 4, 1]


@lru_cache(maxsize=10)
def matrix_141(n: int) -> Matrix:
    """Get matrix '1 4 1'."""

    m = [[0] * n for _ in range(n)]  # type: Matrix
    m[0][0:2] = M141[1:]
    m[-1][-2:] = M141[:-1]
    for x in range(n - 2):
        m[x + 1][x:x + 3] = M141
    return alg.inv(m)


class InterpolatorNaturalBSpline(InterpolatorBSpline):
    """Natural B-spline class."""

    def setup(self) -> None:
        """
        Using B-spline as the base create a natural spline that also passes through the control points.

        Using the color points as `S0...Sn`, calculate `B0...Bn`, such that interpolation will
        pass through `S0...Sn`.

        When given 2 data points, the operation will be linear, so there is nothing to do.
        """

        # Use the same logic as normal B-spline for handling undefined values and applying premultiplication
        self.handle_undefined()

        n = self.length - 2

        # Special case 3 data points
        if n == 1:
            self.coordinates[1] = [
                (a * 6 - (b + c)) / 4 for a, b, c in zip(self.coordinates[1], self.coordinates[0], self.coordinates[2])
            ]

        # Handle all other cases where n does not result in linear interpolation
        elif n > 1:
            # Create [1, 4, 1] matrix
            m = matrix_141(n)

            # Create C matrix from the data points
            c = []
            for r in range(1, n + 1):
                if r == 1:
                    c.append([a * 6 - b for a, b in zip(self.coordinates[r], self.coordinates[r - 1])])
                elif r == n:
                    c.append([a * 6 - b for a, b in zip(self.coordinates[n], self.coordinates[n + 1])])
                else:
                    c.append([a * 6 for a in self.coordinates[r]])

            # Dot M^-1 and C to get B (control points)
            v = alg.dot(m, c)
            for r in range(1, n + 1):
                self.coordinates[r] = v[r - 1]

        self.adjust_endpoints()


class NaturalBSpline(Interpolate):
    """Natural B-spline interpolation plugin."""

    NAME = "natural"

    def interpolator(
        self,
        coordinates: List[Vector],
        channel_names: Sequence[str],
        create: Type['Color'],
        easings: List[Optional[Callable[..., float]]],
        stops: Dict[int, float],
        space: str,
        out_space: str,
        progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
        premultiplied: bool,
        extrapolate: bool = False,
        **kwargs: Any
    ) -> Interpolator:
        """Return the natural B-spline interpolator."""

        return InterpolatorNaturalBSpline(
            coordinates,
            channel_names,
            create,
            easings,
            stops,
            space,
            out_space,
            progress,
            premultiplied,
            extrapolate
        )
