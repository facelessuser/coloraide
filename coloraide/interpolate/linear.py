"""Piecewise linear interpolation."""
from .. import algebra as alg
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Optional, Callable, Mapping, Union, Any, Type, Sequence, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class InterpolatorLinear(Interpolator):
    """Interpolate multiple ranges of colors using linear, Piecewise interpolation."""

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
                value = alg.lerp(c1, c2, t)
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
