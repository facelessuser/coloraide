"""Piecewise linear interpolation."""
from __future__ import annotations
import math
from .. import algebra as alg
from . import Interpolator, Interpolate
from ..types import Vector, AnyColor
from typing import Any


class InterpolatorLinear(Interpolator[AnyColor]):
    """Interpolate multiple ranges of colors using linear, Piecewise interpolation."""

    def normalize_hue(
        self,
        color1: Vector,
        color2: Vector,
        hue: str
    ) -> None:
        """
        Adjust hues.

        Undefined hues are not resolved at this point in time.
        When interpolating between achromatic colors, hue specifications
        such as shorter and longer will have no affect as undefined hues
        will remain undefined meaning there is no arc length to choose
        between. This gives more intuitive interpolation results.
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

        mx = self.max_hue
        half = self.half_hue

        c1 %= mx
        c2 %= mx

        if hue == "shorter":
            if c2 - c1 > half:
                c1 += mx
            elif c2 - c1 < -half:
                c2 += mx

        elif hue == "longer":
            if 0 < (c2 - c1) < half:
                c1 += mx
            elif -half < (c2 - c1) <= 0:
                c2 += mx

        elif hue == "increasing":
            if c2 < c1:
                c2 += mx

        elif hue == "decreasing":
            if c1 < c2:
                c1 += mx

        else:
            raise ValueError(f"Unknown hue adjuster '{hue}'")

        color1[index] = c1
        color2[index] = c2


    def setup(self) -> None:
        """Setup for linear interpolation."""

        end = self.length - 2

        i = 0
        while i <= end:
            c1, c2 = self.coordinates[i:i + 2]

            # Piecewise interpolation will evaluate the same color two different ways
            # if sandwiched between two other colors. Create pairs and evaluate
            # the undefined values and premultiplied states with this context.
            if i < end:
                self.coordinates.insert(i + 2, c2[:])
                end += 1

            if self.hue_index >= 0:
                self.normalize_hue(c1, c2, self.hue)
                self.coordinates[i:i + 2] = [c1, c2]

            # Handle non-hue undefined values.
            for j in range(len(c1)):
                if j != self.hue_index:
                    na, nb = math.isnan(c1[j]), math.isnan(c2[j])
                    if na and nb:
                        continue
                    if na:
                        c1[j] = c2[j]
                    elif nb:
                        c2[j] = c1[j]

            # Premultiply alpha if required and the color has a valid alpha.
            if self.premultiplied:
                if not math.isnan(c1[-1]):
                    self.premultiply(c1)
                if not math.isnan(c2[-1]):
                    self.premultiply(c2)

            i += 2

    def interpolate(
        self,
        point: float,
        index: int
    ) -> Vector:
        """Interpolate."""

        # Interpolate between the values of the two colors for each channel.
        channels = []
        i = (index - 1) * 2

        for i, values in enumerate(zip(*self.coordinates[i:i + 2])):  # noqa: B020
            a, b = values

            # Both values are undefined, so return undefined
            if math.isnan(a) and math.isnan(b):
                value = math.nan

            # Using linear interpolation between the two points
            else:
                # Interpolate
                value = alg.lerp(a, b, self.ease(point, i))
            channels.append(value)

        return channels


class Linear(Interpolate):
    """Linear interpolation plugin."""

    NAME = "linear"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator[AnyColor]:
        """Return the linear interpolator."""

        return InterpolatorLinear(*args, **kwargs)
