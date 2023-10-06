"""Monotone interpolation based on a Hermite interpolation spline."""
from __future__ import annotations
from .bspline import InterpolatorBSpline
from ..interpolate import Interpolator, Interpolate
from .. import algebra as alg
from typing import Any


class InterpolatorMonotone(InterpolatorBSpline):
    """Interpolate with monotone spline based on Hermite."""

    def setup(self) -> None:
        """Setup."""

        super().setup()
        self.spline = alg.monotone


class Monotone(Interpolate):
    """Monotone interpolation plugin."""

    NAME = "monotone"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator:
        """Return the monotone interpolator."""

        return InterpolatorMonotone(*args, **kwargs)
