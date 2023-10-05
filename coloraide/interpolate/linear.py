"""Piecewise linear interpolation."""
from __future__ import annotations
import math
from .. import algebra as alg
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Any


class InterpolatorLinear(Interpolator):
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

        if hue == "specified":
            return

        c1 %= 360
        c2 %= 360

        if math.isnan(c1) or math.isnan(c2):
            return

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

            # If we have a NaN for one alpha and the other alpha is not
            # Use the non-NaN alpha, but if we are premultiplied, we need
            # to now premultiply that coordinate set.
            if self.premultiplied:
                a, b = c1[-1], c2[-1]
                a_nan, b_nan = math.isnan(a), math.isnan(b)

                # Premultiply the alpha
                if not a_nan:
                    self.premultiply(c1)

                    # Mirror the alpha of its sibling as it has no alpha
                    if b_nan:
                        self.premultiply(c2, a)

                # Premultiply the alpha
                if not b_nan:
                    self.premultiply(c2)

                    # Mirror the alpha of its sibling as it has no alpha
                    if a_nan:
                        self.premultiply(c1, b)

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

            # One channel is undefined, take the one that is not
            elif math.isnan(a):
                value = b
            elif math.isnan(b):
                value = a

            # Using linear interpolation between the two points
            else:
                # Interpolate
                value = alg.lerp(a, b, self.ease(point, i))
            channels.append(value)

        return channels


class Linear(Interpolate):
    """Linear interpolation plugin."""

    NAME = "linear"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator:
        """Return the linear interpolator."""

        return InterpolatorLinear(*args, **kwargs)
