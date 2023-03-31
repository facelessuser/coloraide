"""Continuous interpolation."""
from __future__ import annotations
from .. import algebra as alg
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Callable, Mapping, Sequence, Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class InterpolatorContinuous(Interpolator):
    """Interpolate with continuous piecewise."""

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

        # Process each set of coordinates
        alpha = len(coords[0]) - 1
        for i in range(len(coords[0])):
            backfill = None
            last = None

            # Process a specific channel for all coordinates sets
            for x in range(1, len(coords)):
                c1, c2 = coords[x - 1:x + 1]
                a, b = c1[i], c2[i]
                a_nan, b_nan = alg.is_nan(a), alg.is_nan(b)

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
        i = index - 2 if index == self.length else index - 1

        for i, values in enumerate(zip(*self.coordinates[i:i + 2])):
            a, b = values

            # Interpolate
            value = alg.lerp(a, b, self.ease(point, i))
            channels.append(value)

        return channels


class Continuous(Interpolate):
    """Continuous interpolation plugin."""

    NAME = "continuous"

    def interpolator(
        self,
        coordinates: list[Vector],
        channel_names: Sequence[str],
        create: type[Color],
        easings: list[Callable[..., float] | None],
        stops: dict[int, float],
        space: str,
        out_space: str,
        progress: Mapping[str, Callable[..., float]] | Callable[..., float] | None,
        premultiplied: bool,
        extrapolate: bool = False,
        domain: list[float] | None = None,
        **kwargs: Any
    ) -> Interpolator:
        """Return the B-spline interpolator."""

        return InterpolatorContinuous(
            coordinates,
            channel_names,
            create,
            easings,
            stops,
            space,
            out_space,
            progress,
            premultiplied,
            extrapolate,
            domain,
            **kwargs
        )
