"""
B-Spline interpolation.

https://en.wikipedia.org/wiki/B-spline
https://www.math.ucla.edu/~baker/149.1.02w/handouts/dd_splines.pdf
http://www2.cs.uregina.ca/~anima/408/Notes/Interpolation/UniformBSpline.htm
"""
from __future__ import annotations
from .. import algebra as alg
from .continuous import InterpolatorContinuous
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Callable, Mapping, Sequence, Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class InterpolatorBSpline(InterpolatorContinuous):
    """Interpolate with B-spline."""

    def adjust_endpoints(self) -> None:
        """Adjust endpoints such that they are clamped and can handle extrapolation."""

        # We cannot interpolate all the way to `coord[0]` and `coord[-1]` without additional control
        # points to coax the curve through the end points. Generate a point at both ends so that we
        # can properly evaluate the spline from start to finish. Additionally, when the extrapolating
        # past the 0 - 1 boundary, provide some linear behavior
        self.extrapolated = [
            list(zip(self.coordinates[0], self.coordinates[1])),
            list(zip(self.coordinates[-2], self.coordinates[-1]))
        ]
        self.coordinates.insert(0, [2 * a - b for a, b in zip(self.coordinates[0], self.coordinates[1])])
        self.coordinates.append([2 * a - b for a, b in zip(self.coordinates[-1], self.coordinates[-2])])

    def setup(self) -> None:
        """Optional setup."""

        # Process undefined values
        self.spline = alg.bspline
        self.handle_undefined()
        self.adjust_endpoints()

    def interpolate(
        self,
        point: float,
        index: int
    ) -> Vector:
        """Interpolate."""

        # Prepare in-boundary coordinates
        coords = list(zip(*self.coordinates[index - 1:index + 3]))

        # Apply interpolation to each channel
        channels = []
        for i in range(len(self.coordinates[0])):

            t = self.ease(point, i)

            # If `t` ends up spilling out past our boundaries, we need to extrapolate
            if self.extrapolate and index == 1 and point < 0.0:
                p0, p1 = self.extrapolated[0][i]
                channels.append(alg.lerp(p0, p1, t))
            elif self.extrapolate and index == self.length - 1 and point > 1.0:
                p0, p1 = self.extrapolated[1][i]
                channels.append(alg.lerp(p0, p1, t))
            else:
                p0, p1, p2, p3 = coords[i]
                channels.append(self.spline(p0, p1, p2, p3, t))

        # Small adjustment for floating point math and alpha channels
        if 1 - channels[-1] < 1e-6:
            channels[-1] = 1

        return channels


class BSpline(Interpolate):
    """B-spline interpolation plugin."""

    NAME = "bspline"

    def interpolator(
        self,
        coordinates: list[Vector],
        channel_names: Sequence[str],
        create: type[Color],
        easings: list[Callable[..., float] | None],
        stops: dict[int, float],
        space: str,
        out_space: str,
        progress: Mapping[str, Callable[..., float]] | Callable[..., float] | None,
        premultiplied: bool,
        extrapolate: bool = False,
        domain: list[float] | None = None,
        **kwargs: Any
    ) -> Interpolator:
        """Return the B-spline interpolator."""

        return InterpolatorBSpline(
            coordinates,
            channel_names,
            create,
            easings,
            stops,
            space,
            out_space,
            progress,
            premultiplied,
            extrapolate,
            domain,
            **kwargs
        )
