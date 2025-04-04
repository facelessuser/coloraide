"""Monotone interpolation based on a Hermite interpolation spline."""
from __future__ import annotations
from .bspline import InterpolatorBSpline
from ..interpolate import Interpolator, Interpolate
from .. import algebra as alg
from .. types import AnyColor
from typing import Any


class InterpolatorMonotone(InterpolatorBSpline[AnyColor]):
    """Interpolate with monotone spline based on Hermite."""

    def setup(self) -> None:
        """Setup."""

        super().setup()
        self.spline = alg.monotone


class Monotone(Interpolate[AnyColor]):
    """Monotone interpolation plugin."""

    NAME = "monotone"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator[AnyColor]:
        """Return the monotone interpolator."""

        return InterpolatorMonotone(*args, **kwargs)
