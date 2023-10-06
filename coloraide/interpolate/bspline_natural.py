"""
Natural B-Spline interpolation.

https://www.math.ucla.edu/~baker/149.1.02w/handouts/dd_splines.pdf.
"""
from __future__ import annotations
from .. interpolate import Interpolate, Interpolator
from .bspline import InterpolatorBSpline
from .. import algebra as alg
from typing import Any


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
        self.spline = alg.bspline
        self.handle_undefined()
        alg.naturalize_bspline_controls(self.coordinates)
        self.adjust_endpoints()


class NaturalBSpline(Interpolate):
    """Natural B-spline interpolation plugin."""

    NAME = "natural"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator:
        """Return the natural B-spline interpolator."""

        return InterpolatorNaturalBSpline(*args, **kwargs)
