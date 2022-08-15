"""Monotone interpolation based on a Hermite interpolation spline."""
from .bspline import InterpolatorBSpline
from ..interpolate import Interpolator, Interpolate
from .. import algebra as alg
from ..types import Vector
from typing import Optional, Callable, Mapping, List, Union, Sequence, Dict, Any, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class InterpolatorMonotone(InterpolatorBSpline):
    """Interpolate with monotone spline based on Hermite."""

    def calculate(self, p0: float, p1: float, p2: float, p3: float, t: float) -> float:
        """Calculate spline."""

        return alg.monotone(p0, p1, p2, p3, t)


class Monotone(Interpolate):
    """Monotone interpolation plugin."""

    NAME = "monotone"

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
        extrapolate: bool = False,
        **kwargs: Any
    ) -> Interpolator:
        """Return the monotone interpolator."""

        return InterpolatorMonotone(
            coordinates,
            channel_names,
            create,
            easings,
            stops,
            space,
            out_space,
            progress,
            premultiplied,
            extrapolate
        )
