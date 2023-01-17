"""
Natural B-Spline interpolation.

https://www.math.ucla.edu/~baker/149.1.02w/handouts/dd_splines.pdf.
"""
from __future__ import annotations
from .. interpolate import Interpolate, Interpolator
from .bspline import InterpolatorBSpline
from .. import algebra as alg
from ..types import Vector
from typing import List, Sequence, Any, Optional, Union, Mapping, Callable, Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class InterpolatorNaturalBSpline(InterpolatorBSpline):
    """Natural B-spline class."""

    def setup(self) -> None:
        """
        Using B-spline as the base create a natural spline that also passes through the control points.

        Using the color points as `S0...Sn`, calculate `B0...Bn`, such that interpolation will
        pass through `S0...Sn`.

        When given 2 data points, the operation will be linear, so there is nothing to do.
        """

        # Use the same logic as normal B-spline for handling undefined values and applying premultiplication
        self.spline = alg.bspline
        self.handle_undefined()
        alg.naturalize_bspline_controls(self.coordinates)
        self.adjust_endpoints()


class NaturalBSpline(Interpolate):
    """Natural B-spline interpolation plugin."""

    NAME = "natural"

    def interpolator(
        self,
        coordinates: List[Vector],
        channel_names: Sequence[str],
        create: Type[Color],
        easings: List[Optional[Callable[..., float]]],
        stops: Dict[int, float],
        space: str,
        out_space: str,
        progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
        premultiplied: bool,
        extrapolate: bool = False,
        domain: Optional[list[float]] = None,
        **kwargs: Any
    ) -> Interpolator:
        """Return the natural B-spline interpolator."""

        return InterpolatorNaturalBSpline(
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
