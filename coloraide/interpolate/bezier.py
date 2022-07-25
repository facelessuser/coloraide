"""Bezier interpolation."""
from .. import algebra as alg
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Optional, Callable, Mapping, List, Union, Type


def binomial_row(n: int) -> List[int]:
    """
    Binomial row.

    Return row in Pascal's triangle.
    """

    row = [1, 1]
    for _ in range(n - 1):
        r = [1]
        x = 0
        for x in range(1, len(row)):
            r.append(row[x] + row[x - 1])
        r.append(row[x])
        row = r
    return row


def handle_undefined(coords: Vector) -> Vector:
    """Handle null values."""

    backfill = None
    for x in range(1, len(coords)):
        a = coords[x - 1]
        b = coords[x]
        if alg.is_nan(a) and not alg.is_nan(b):
            coords[x - 1] = b
        elif alg.is_nan(b) and not alg.is_nan(a):
            coords[x] = a
        elif alg.is_nan(a) and alg.is_nan(b):
            # Multiple undefined values, mark the start
            backfill = x - 1
            continue

        # Replace all undefined values that occurred prior to
        # finding the current defined value
        if backfill is not None:
            coords[backfill:x - 1] = [b] * (x - 1 - backfill)
            backfill = None

    return coords


class InterpolatorBezier(Interpolator):
    """Interpolate Bezier."""

    def interpolate(
        self,
        easing: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
        point: float,
        index: int
    ) -> Vector:
        """Interpolate."""

        # Bezier interpolates against all colors, so make point absolute
        piece = 1 / (self.length - 1)
        first = (index - 1) * piece
        last = index * piece
        self.index = index

        # Get row from Pascal's Triangle
        n = self.length - 1
        row = binomial_row(n)

        # Use Bezier interpolation of all color for each channel
        channels = []
        for i, coords in enumerate(zip(*self.coordinates)):

            # Do we have an easing function, or mapping with a channel easing function?
            progress = None
            name = self.names[i]
            if isinstance(easing, Mapping):
                progress = easing.get(name)
                if progress is None:
                    progress = easing.get('all')
            else:
                progress = easing

            # Apply easing and scale properly between the colors
            t = alg.clamp(point if progress is None else progress(point), 0.0, 1.0)
            t = t * (last - first) + first

            x = 1 - t
            s = 0.0
            for j, c in enumerate(handle_undefined(list(coords)), 0):
                s += row[j] * (x ** (n - j)) * (t ** j) * c

            channels.append(s)

        return channels


class InterpolateBezier(Interpolate):
    """Bezier interpolation plugin."""

    NAME = "bezier"

    def get_interpolator(self) -> Type[Interpolator]:
        """Return the Bezier interpolator."""

        return InterpolatorBezier
