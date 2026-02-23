"""Luminance preserving scale."""
from __future__ import annotations
from .fit_scale import Scale
from . import scale_rgb
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .. import Color


class ScaleLuminance(Scale):
    """Luminance preserving scale."""

    NAME = 'scale-luminance'

    def fit(
        self,
        color: Color,
        space: str,
        preserve_luminance: bool = True,
        **kwargs: Any
    ) -> None:
        """Scale the color within its gamut but preserve L and h as much as possible."""

        scale_rgb(color, scale_space=space, preserve_luminance=preserve_luminance, **kwargs)
