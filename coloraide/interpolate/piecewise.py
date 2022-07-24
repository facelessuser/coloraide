"""Piecewise linear interpolation."""
from .. import algebra as alg
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Optional, Callable, Mapping, Union, Type


class InterpolatorPiecewise(Interpolator):
    """Interpolate multiple ranges of colors."""

    def interpolate(
        self,
        easing: Optional[Union[Callable[..., float], Mapping[str, Callable[..., float]]]],
        point: float,
        index: int
    ) -> Vector:
        """Interpolate."""

        # Interpolate between the values of the two colors for each channel.
        channels = []
        for i, values in enumerate(zip(*self.coordinates[index - 1:index + 1])):
            c1, c2 = values

            # Both values are undefined, so return undefined
            if alg.is_nan(c1) and alg.is_nan(c2):
                value = alg.NaN

            # One channel is undefined, take the one that is not
            elif alg.is_nan(c1):
                value = c2
            elif alg.is_nan(c2):
                value = c1

            # Using linear interpolation between the two points
            else:
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

                # Interpolate
                value = alg.lerp(c1, c2, t)
            channels.append(value)

        return channels


class InterpolatePiecewise(Interpolate):
    """Linear piecewise interpolation plugin."""

    NAME = "linear"

    def get_interpolator(self) -> Type[Interpolator]:
        """Return the linear piecewise interpolator."""

        return InterpolatorPiecewise
