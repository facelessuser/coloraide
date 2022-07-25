"""B-Spline interpolation."""
from .. import algebra as alg
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Optional, Callable, Mapping, List, Union, Sequence, Dict, Any, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def handle_undefined(coords: List[Vector]) -> None:
    """Handle null values."""

    # Process each set of coordinates
    for i in range(len(coords[0])):
        backfill = None
        # Process a specific channel for all coordinates sets
        for x in range(1, len(coords)):
            c1, c2 = coords[x - 1:x + 1]
            a, b = c1[i], c2[i]
            if alg.is_nan(a) and not alg.is_nan(b):
                c1[i] = b
            elif alg.is_nan(b) and not alg.is_nan(a):
                c2[i] = a
            elif alg.is_nan(a) and alg.is_nan(b):
                # Multiple undefined values, mark the start
                backfill = x - 1
                continue

            # Replace all undefined values that occurred prior to
            # finding the current defined value
            if backfill is not None:
                for c in coords[backfill:x - 1]:
                    c[i] = b
                backfill = None


class InterpolatorBspline(Interpolator):
    """Interpolate with B-spline."""

    def __init__(
        self,
        coordinates: List[Vector],
        names: Sequence[str],
        create: Type['Color'],
        easings: List[Optional[Callable[..., float]]],
        stops: Dict[int, float],
        space: str,
        out_space: str,
        progress: Optional[Union[Callable[..., float], Mapping[str, Callable[..., float]]]],
        premultiplied: bool,
        **kwargs: Any
    ):
        """Initialize."""

        super().__init__(
            coordinates,
            names,
            create,
            easings,
            stops,
            space,
            out_space,
            progress,
            premultiplied,
            **kwargs
        )

        # Process undefined values
        handle_undefined(self.coordinates)

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
