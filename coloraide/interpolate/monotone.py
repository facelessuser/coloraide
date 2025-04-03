"""Monotone interpolation based on a Hermite interpolation spline."""
from __future__ import annotations
from .bspline import InterpolatorBSpline
from ..interpolate import Interpolator, Interpolate
from .. import algebra as alg
from .. types import TypeColor
from typing import Any


class InterpolatorMonotone(InterpolatorBSpline[TypeColor]):
    """Interpolate with monotone spline based on Hermite."""

    def setup(self) -> None:
        """Setup."""

        super().setup()
        self.spline = alg.monotone


class Monotone(Interpolate[TypeColor]):
    """Monotone interpolation plugin."""

    NAME = "monotone"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator[TypeColor]:
        """Return the monotone interpolator."""

        return InterpolatorMonotone(*args, **kwargs)
