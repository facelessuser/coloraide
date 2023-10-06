"""Piecewise linear interpolation."""
from __future__ import annotations
import math
from .linear import InterpolatorLinear
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Any


class InterpolatorCSSLinear(InterpolatorLinear):
    """Interpolate multiple ranges of colors using linear, Piecewise interpolation, but adhere to CSS requirements."""

    def normalize_hue(
        self,
        color1: Vector,
        color2: Vector,
        hue: str
    ) -> None:
        """
        Adjust hues.

        Hues are applied to match CSS. This means the undefined hues are resolved
        before fix-up such that during hue-fix, undefined hues will assume the value
        of the other color (if the hue is defined) creating an arc length. Since
        interpolation between a non-achromatic color and achromatic color will
        now have a false arc length, hue specifications such as shorter and longer
        will produce different results in such cases. This is done purposely in
        CSS.

        In non-CSS linear interpolation, undefined hue resolution is performed later
        and yields a result that such that their is no hue arc which gives more
        intuitive results with achromatic colors.
        """

        index = self.hue_index

        c1 = color1[index]
        c2 = color2[index]

        is_nan1 = math.isnan(c1)
        is_nan2 = math.isnan(c2)

        if is_nan1 and is_nan2:
            return
        elif is_nan1:
            c1 = c2
        elif is_nan2:
            c2 = c1

        if hue == "specified":
            return

        c1 %= 360
        c2 %= 360

        if hue == "shorter":
            if c2 - c1 > 180:
                c1 += 360
            elif c2 - c1 < -180:
                c2 += 360

        elif hue == "longer":
            if 0 < (c2 - c1) < 180:
                c1 += 360
            elif -180 < (c2 - c1) <= 0:
                c2 += 360

        elif hue == "increasing":
            if c2 < c1:
                c2 += 360

        elif hue == "decreasing":
            if c1 < c2:
                c1 += 360

        else:
            raise ValueError("Unknown hue adjuster '{}'".format(hue))

        color1[index] = c1
        color2[index] = c2


class CSSLinear(Interpolate):
    """CSS Linear interpolation plugin."""

    NAME = "css-linear"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator:
        """Return the CSS linear interpolator."""

        return InterpolatorCSSLinear(*args, **kwargs)
