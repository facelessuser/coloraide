"""
Catmull-Rom interpolation.

http://www2.cs.uregina.ca/~anima/408/Notes/Interpolation/Parameterized-Curves-Summary.htm
"""
from __future__ import annotations
from .bspline import InterpolatorBSpline
from ..interpolate import Interpolator, Interpolate
from .. import algebra as alg
from .. types import ColorType
from typing import Any


class InterpolatorCatmullRom(InterpolatorBSpline[ColorType]):
    """Interpolate with Catmull-Rom spline."""

    def setup(self) -> None:
        """Setup."""

        super().setup()
        self.spline = alg.catrom


class CatmullRom(Interpolate[ColorType]):
    """Catmull-Rom interpolation plugin."""

    NAME = "catrom"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator[ColorType]:
        """Return the Catmull-Rom interpolator."""

        return InterpolatorCatmullRom(*args, **kwargs)
