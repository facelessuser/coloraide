"""A scaling approach that preserves luminance."""
from __future__ import annotations
from . import Fit, scale_rgb
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .. import Color


class Scale(Fit):
    """Gamut mapping by using ray tracing."""

    NAME = "scale"

    def fit(
        self,
        color: Color,
        space: str,
        **kwargs: Any
    ) -> None:
        """Scale the color within its gamut but preserve L and h as much as possible."""

        scale_rgb(color, scale_space=space, **kwargs)
