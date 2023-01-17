"""
B-Spline interpolation.

https://en.wikipedia.org/wiki/B-spline
https://www.math.ucla.edu/~baker/149.1.02w/handouts/dd_splines.pdf
http://www2.cs.uregina.ca/~anima/408/Notes/Interpolation/UniformBSpline.htm
"""
from __future__ import annotations
from .. import algebra as alg
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Optional, Callable, Mapping, Sequence, Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class InterpolatorBSpline(Interpolator):
    """Interpolate with B-spline."""

    def handle_undefined(self) -> None:
        """
        Handle null values.

        Resolve any undefined alpha values and apply premultiplication if necessary.

        Additionally, any undefined value have a new control point generated via
        linear interpolation. This is the only approach to provide a non-bias, non-breaking
        way to handle things like achromatic hues in a cylindrical space. It also balances
        not cylindrical values. Since the B-spline needs a a continual path and since we
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

    def adjust_endpoints(self) -> None:
        """Adjust endpoints such that they are clamped and can handle extrapolation."""

        # We cannot interpolate all the way to `coord[0]` and `coord[-1]` without additional control
        # points to coax the curve through the end points. Generate a point at both ends so that we
        # can properly evaluate the spline from start to finish. Additionally, when the extrapolating
        # past the 0 - 1 boundary, provide some linear behavior
        self.extrapolated = [
            list(zip(self.coordinates[0], self.coordinates[1])),
            list(zip(self.coordinates[-2], self.coordinates[-1]))
        ]
        self.coordinates.insert(0, [2 * a - b for a, b in zip(self.coordinates[0], self.coordinates[1])])
        self.coordinates.append([2 * a - b for a, b in zip(self.coordinates[-1], self.coordinates[-2])])

    def setup(self) -> None:
        """Optional setup."""

        # Process undefined values
        self.spline = alg.bspline
        self.handle_undefined()
        self.adjust_endpoints()

    def interpolate(
        self,
        point: float,
        index: int
    ) -> Vector:
        """Interpolate."""

        # Prepare in-boundary coordinates
        coords = list(zip(*self.coordinates[index - 1:index + 3]))

        # Apply interpolation to each channel
        channels = []
        for i in range(len(self.coordinates[0])):

            t = self.ease(point, i)

            # If `t` ends up spilling out past our boundaries, we need to extrapolate
            if self.extrapolate and index == 1 and point < 0.0:
                p0, p1 = self.extrapolated[0][i]
                channels.append(alg.lerp(p0, p1, t))
            elif self.extrapolate and index == self.length - 1 and point > 1.0:
                p0, p1 = self.extrapolated[1][i]
                channels.append(alg.lerp(p0, p1, t))
            else:
                p0, p1, p2, p3 = coords[i]
                channels.append(self.spline(p0, p1, p2, p3, t))

        # Small adjustment for floating point math and alpha channels
        if 1 - channels[-1] < 1e-6:
            channels[-1] = 1

        return channels


class BSpline(Interpolate):
    """B-spline interpolation plugin."""

    NAME = "bspline"

    def interpolator(
        self,
        coordinates: list[Vector],
        channel_names: Sequence[str],
        create: type[Color],
        easings: list[Optional[Callable[..., float]]],
        stops: dict[int, float],
        space: str,
        out_space: str,
        progress: Optional[Mapping[str, Callable[..., float]] | Callable[..., float]],
        premultiplied: bool,
        extrapolate: bool = False,
        domain: Optional[list[float]] = None,
        **kwargs: Any
    ) -> Interpolator:
        """Return the B-spline interpolator."""

        return InterpolatorBSpline(
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
            domain
        )
