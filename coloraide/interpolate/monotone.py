"""Monotone interpolation based on a Hermite interpolation spline."""
from __future__ import annotations
from .bspline import InterpolatorBSpline
from . import Interpolator, Interpolate
from .. import algebra as alg
from .. types import AnyColor
from typing import Any


class InterpolatorMonotone(InterpolatorBSpline[AnyColor]):
    """Interpolate with monotone spline based on Hermite."""

    def setup(self) -> None:
        """Setup."""

        self.handle_undefined()
        self.spline = alg.MonotoneInterpolator
        self.spline.preprocess(self.coordinates)


class Monotone(Interpolate[AnyColor]):
    """Monotone interpolation plugin."""

    NAME = "monotone"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator[AnyColor]:
        """Return the monotone interpolator."""

        return InterpolatorMonotone(*args, **kwargs)
