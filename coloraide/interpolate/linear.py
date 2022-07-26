"""Piecewise linear interpolation."""
from .. import algebra as alg
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Optional, Callable, Mapping, Union, Any, Type, Sequence, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class InterpolatorLinear(Interpolator):
    """Interpolate multiple ranges of colors using linear, Piecewise interpolation."""

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

            # If we have a NaN for one alpha and the other alpha is not
            # Use the non-NaN alpha, but if we are premultiplied, we need
            # to now premultiply that coordinate set.
            if self.premultiplied:
                a, b = c1[-1], c2[-1]
                a_nan, b_nan = alg.is_nan(a), alg.is_nan(b)

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
        easing: Optional[Union[Callable[..., float], Mapping[str, Callable[..., float]]]],
        point: float,
        index: int
    ) -> Vector:
        """Interpolate."""

        # Interpolate between the values of the two colors for each channel.
        channels = []
        i = (index - 1) * 2

        for i, values in enumerate(zip(*self.coordinates[i:i + 2])):
            a, b = values

            # Both values are undefined, so return undefined
            if alg.is_nan(a) and alg.is_nan(b):
                value = alg.NaN

            # One channel is undefined, take the one that is not
            elif alg.is_nan(a):
                value = b
            elif alg.is_nan(b):
                value = a

            # Using linear interpolation between the two points
            else:
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

                # Interpolate
                value = alg.lerp(a, b, t)
            channels.append(value)

        return channels


class Linear(Interpolate):
    """Linear interpolation plugin."""

    NAME = "linear"

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
        """Return the linear interpolator."""

        return InterpolatorLinear(
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
