"""Monotone interpolation based on a Hermite interpolation spline."""
from __future__ import annotations
from .bspline import InterpolatorBSpline
from ..interpolate import Interpolator, Interpolate
from .. import algebra as alg
from ..types import Vector
from typing import Optional, Callable, Mapping, Sequence, Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class InterpolatorMonotone(InterpolatorBSpline):
    """Interpolate with monotone spline based on Hermite."""

    def setup(self) -> None:
        """Setup."""

        super().setup()
        self.spline = alg.monotone


class Monotone(Interpolate):
    """Monotone interpolation plugin."""

    NAME = "monotone"

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
            extrapolate,
            domain
        )
