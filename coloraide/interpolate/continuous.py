"""Continuous interpolation."""
from __future__ import annotations
import math
from .. import algebra as alg
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Any


def adjust_shorter(h1: float, h2: float, offset: float) -> tuple[float, float]:
    """Adjust the given hues."""

    d = h2 - h1
    if d > 180:
        h2 -= 360.0
        offset -= 360.0
    elif d < -180:
        h2 += 360
        offset += 360.0
    return h2, offset


def adjust_longer(h1: float, h2: float, offset: float) -> tuple[float, float]:
    """Adjust the given hues."""

    d = h2 - h1
    if 0 < d < 180:
        h2 -= 360.0
        offset -= 360.0
    elif -180 < d <= 0:
        h2 += 360
        offset += 360.0
    return h2, offset


def adjust_increase(h1: float, h2: float, offset: float) -> tuple[float, float]:
    """Adjust the given hues."""

    if h2 < h1:
        h2 += 360.0
        offset += 360.0
    return h2, offset


def adjust_decrease(h1: float, h2: float, offset: float) -> tuple[float, float]:
    """Adjust the given hues."""

    if h2 > h1:
        h2 -= 360.0
        offset -= 360.0
    return h2, offset


class InterpolatorContinuous(Interpolator):
    """Interpolate with continuous piecewise."""

    def normalize_hue(
        self,
        color1: Vector,
        color2: Vector | None,
        offset: float,
        hue: str,
        fallback: float | None
    ) -> tuple[Vector, float]:
        """
        Normalize hues according the hue specifier.

        Hues are normalized in a continuous way such that the fix-up is applied
        relative to the hues that come before it.
        """

        index = self.hue_index

        if hue == 'specified':
            return (color2 or color1), offset

        # Probably the first hue
        if color2 is None:
            color1[index] = color1[index] % 360
            return color1, offset

        if hue == 'shorter':
            adjuster = adjust_shorter
        elif hue == 'longer':
            adjuster = adjust_longer
        elif hue == 'increasing':
            adjuster = adjust_increase
        elif hue == 'decreasing':
            adjuster = adjust_decrease
        else:
            raise ValueError("Unknown hue adjuster '{}'".format(hue))

        c1 = color1[index] + offset
        c2 = (color2[index] % 360) + offset

        # Adjust hue, handle gaps across `NaN`s
        if not math.isnan(c2):
            if not math.isnan(c1):
                c2, offset = adjuster(c1, c2, offset)
            elif fallback is not None:
                c2, offset = adjuster(fallback, c2, offset)

        color2[index] = c2
        return color2, offset

    def handle_undefined(self) -> None:
        """
        Handle null values.

        Resolve any undefined alpha values and apply premultiplication if necessary.

        Additionally, any undefined value have a new control point generated via
        linear interpolation. This is the only approach to provide a non-bias, non-breaking
        way to handle things like achromatic hues in a cylindrical space. It also balances
        non cylindrical values. Since the B-spline needs a a continual path and since we
        have a sliding window that takes into account 4 points at a time, we must consider
        a more broad context than what is done in piecewise linear.
        """

        coords = self.coordinates
        end = self.length - 2
        hue_index = self.hue_index

        # Normalize hue
        offset = 0.0
        fallback = None
        if hue_index >= 0:
            first = self.coordinates[0]
            h = first[hue_index]
            self.coordinates[0], offset = self.normalize_hue(first, None, offset, self.hue, fallback)
            if not math.isnan(h):
                fallback = h

        i = 0
        while i <= end:
            c1, c2 = self.coordinates[i:i + 2]
            if hue_index >= 0:
                h = c2[hue_index]
                self.coordinates[i + 1], offset = self.normalize_hue(c1, c2, offset, self.hue, fallback)
                if not math.isnan(h):
                    fallback = h
            i += 1

        # Process each set of coordinates
        alpha = len(coords[0]) - 1
        for i in range(len(coords[0])):
            backfill = None
            last = None

            # Process a specific channel for all coordinates sets
            for x in range(1, len(coords)):
                c1, c2 = coords[x - 1:x + 1]
                a, b = c1[i], c2[i]
                a_nan, b_nan = math.isnan(a), math.isnan(b)

                # Two good values, store the last good value and continue
                if not a_nan and not b_nan:
                    if self.premultiplied and i == alpha:
                        self.premultiply(c1)
                        self.premultiply(c2)
                    last = b
                    continue

                # Found a gap
                if a_nan:
                    # First color starts an undefined gap
                    if backfill is None:
                        backfill = x - 1

                    # Gap continues
                    if b_nan:
                        continue

                    if self.premultiplied and i == alpha:
                        self.premultiply(c2)

                    # Generate new control points for the undefined value. Use linear
                    # interpolation if two known values bookend the undefined gap,
                    # else just backfill the current known value.
                    point = 1 / (x - backfill + 1)
                    for e, c in enumerate(coords[backfill:x], 1):
                        p = alg.lerp(last, b, point * e) if last is not None else b
                        c[i] = p

                        # We just filled an alpha hole, premultiply the coordinates
                        if self.premultiplied and i == alpha:
                            self.premultiply(c)

                    backfill = None
                    last = b
                else:
                    # Started a new gap after a good value
                    # This always starts a new gap and never finishes one
                    if backfill is None:
                        backfill = x

                    if self.premultiplied and i == alpha:
                        self.premultiply(c1)
                    last = a

            # Replace all undefined values that occurred prior to
            # finding the current defined value that have not been backfilled
            if backfill is not None and last is not None:
                for c in coords[backfill:]:
                    c[i] = last

                    # We just filled an alpha hole, premultiply the coordinates
                    if self.premultiplied and i == alpha:
                        self.premultiply(c)

    def setup(self) -> None:
        """Optional setup."""

        # Process undefined values
        self.handle_undefined()

    def interpolate(
        self,
        point: float,
        index: int
    ) -> Vector:
        """Interpolate."""

        # Interpolate between the values of the two colors for each channel.
        channels = []
        idx = index - 2 if index == self.length else index - 1

        for i, values in enumerate(zip(*self.coordinates[idx:idx + 2])):
            a, b = values

            # Interpolate
            value = alg.lerp(a, b, self.ease(point, i))
            channels.append(value)

        return channels


class Continuous(Interpolate):
    """Continuous interpolation plugin."""

    NAME = "continuous"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator:
        """Return the continuous interpolator."""

        return InterpolatorContinuous(*args, **kwargs)
