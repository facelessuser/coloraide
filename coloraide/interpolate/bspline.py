"""
B-Spline interpolation.

https://en.wikipedia.org/wiki/B-spline
https://www.math.ucla.edu/~baker/149.1.02w/handouts/dd_splines.pdf
http://www2.cs.uregina.ca/~anima/408/Notes/Interpolation/UniformBSpline.htm
"""
from __future__ import annotations
from .. import algebra as alg
from .continuous import InterpolatorContinuous
from . import Interpolator, Interpolate
from ..types import Vector, AnyColor
from typing import Any


class InterpolatorBSpline(InterpolatorContinuous[AnyColor]):
    """Interpolate with B-spline."""

    def setup(self) -> None:
        """Optional setup."""

        # Process undefined values
        self.handle_undefined()
        self.spline = alg.BSplineInterpolator
        self.spline.preprocess(self.coordinates)

    def interpolate(
        self,
        point: float,
        index: int
    ) -> Vector:
        """Interpolate."""

        # Prepare in-boundary coordinates
        coords = [*zip(*self.coordinates[index - 1:index + 3])]

        # Apply interpolation to each channel
        channels = []
        for i in range(len(self.coordinates[0])):

            t = self.ease(point, i)

            # If `t` ends up spilling out past our boundaries, we need to extrapolate
            if self.extrapolate and index == 1 and point < 0.0:
                p0, p1 = coords[i][1:3]
                channels.append(alg.lerp(p0, p1, t))
            elif self.extrapolate and index == self.length - 1 and point > 1.0:
                p0, p1 = coords[i][-3:-1]
                channels.append(alg.lerp(p0, p1, t))
            else:
                p0, p1, p2, p3 = coords[i]
                channels.append(self.spline.interpolate(p0, p1, p2, p3, t))

        # Small adjustment for floating point math and alpha channels
        if 1 - channels[-1] < 1e-6:
            channels[-1] = 1

        return channels


class BSpline(Interpolate[AnyColor]):
    """B-spline interpolation plugin."""

    NAME = "bspline"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator[AnyColor]:
        """Return the B-spline interpolator."""

        return InterpolatorBSpline(*args, **kwargs)
