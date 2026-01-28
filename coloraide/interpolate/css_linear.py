"""Piecewise linear interpolation."""
from __future__ import annotations
from .linear import InterpolatorLinear
from ..interpolate import Interpolator, Interpolate
from ..types import AnyColor
from ..deprecate import deprecated
from typing import Any


class CSSLinear(Interpolate[AnyColor]):
    """CSS Linear interpolation plugin."""

    NAME = "css-linear"

    @deprecated(
        "The 'css-linear' interpolator has been deprecated as the 'linear' now works the same, please use 'linear'"
    )
    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator[AnyColor]:  # pragma: no cover
        """Return the CSS linear interpolator."""

        return InterpolatorLinear(*args, **kwargs)
