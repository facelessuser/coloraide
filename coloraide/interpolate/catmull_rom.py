"""
Catmull-Rom interpolation.

http://www2.cs.uregina.ca/~anima/408/Notes/Interpolation/Parameterized-Curves-Summary.htm
"""
from .bspline import InterpolatorBSpline
from ..interpolate import Interpolator, Interpolate
from ..types import Vector
from typing import Optional, Callable, Mapping, List, Union, Sequence, Dict, Any, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class InterpolatorCatmullRom(InterpolatorBSpline):
    """Interpolate with Catmull-Rom spline."""

    def calculate(self, p0: float, p1: float, p2: float, p3: float, t: float) -> float:
        """Calculate the new point using the provided values."""

        # Save some time calculating this once
        t2 = t ** 2
        t3 = t2 * t

        # Insert control points to algorithm
        return (
            (-t3 + 2 * t2 - t) * p0 +  # B0
            (3 * t3 - 5 * t2 + 2) * p1 +  # B1
            (-3 * t3 + 4 * t2 + t) * p2 +  # B2
            (t3 - t2) * p3  # B3
        ) / 2


class CatmullRom(Interpolate):
    """Catmull-Rom interpolation plugin."""

    NAME = "catrom"

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
        """Return the Catmull-Rom interpolator."""

        return InterpolatorCatmullRom(
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
