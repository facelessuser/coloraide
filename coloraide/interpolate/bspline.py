"""B-Spline interpolation."""
from .. import algebra as alg
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Optional, Callable, Mapping, List, Union, Sequence, Dict, Any, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class InterpolatorBspline(Interpolator):
    """Interpolate with B-spline."""

    def handle_undefined(self, coords: List[Vector]) -> None:
        """Handle null values."""

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

                    # If we've seen a good coordinate before the undefined gap,
                    # linearly interpolate the two good values on either side,
                    # else just backfill the current value. This is the only
                    # way to have sane interpolation with achromatic hues.
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
        self.handle_undefined(self.coordinates)

        # We cannot interpolate all the way to `coord[0]` and `coord[-1]` without additional points
        # to coax the curve through the end points. Generate a point at both ends so that we can
        # properly evaluate the spline.
        c1 = self.coordinates[1]
        c2 = self.coordinates[-2]
        self.coordinates.insert(0, [2 * a - b for a, b in zip(self.coordinates[0], c1)])
        self.coordinates.append([2 * a - b for a, b in zip(self.coordinates[-1], c2)])

    def interpolate(
        self,
        easing: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
        point: float,
        index: int
    ) -> Vector:
        """Interpolate."""

        # Use Bezier interpolation of all color for each channel
        channels = []
        for i, coords in enumerate(zip(*self.coordinates)):

            # Do we have an easing function, or mapping with a channel easing function?
            progress = None
            name = self.channel_names[i]
            if isinstance(easing, Mapping):
                progress = easing.get(name)
                if progress is None:
                    progress = easing.get('all')
            else:
                progress = easing

            # Apply easing and scale properly between the colors
            t = alg.clamp(point if progress is None else progress(point), 0.0, 1.0)
            t2 = t ** 2
            t3 = t2 * t

            p0, p1, p2, p3 = coords[index - 1:index + 3]
            channels.append(
                (
                    ((1 - t) ** 3) * p0 +  # B0
                    (3 * t3 - 6 * t2 + 4) * p1 +  # B1
                    (-3 * t3 + 3 * t2 + 3 * t + 1) * p2 +  # B2
                    t3 * p3  # B3
                ) / 6
            )

        return channels


class BSpline(Interpolate):
    """B-spline interpolation plugin."""

    NAME = "b-spline"

    def interpolator(
        self,
        coordinates: List[Vector],
        channel_names: Sequence[str],
        create: Type['Color'],
        easings: List[Optional[Callable[..., float]]],
        stops: Dict[int, float],
        space: str,
        out_space: str,
        progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
        premultiplied: bool,
        **kwargs: Any
    ) -> Interpolator:
        """Return the B-spline interpolator."""

        return InterpolatorBspline(
            coordinates,
            channel_names,
            create,
            easings,
            stops,
            space,
            out_space,
            progress,
            premultiplied
        )
