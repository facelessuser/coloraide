"""
L* color contrast.

Used for color contrast in Google's HCT.

https://material.io/blog/science-of-color-design
"""
from __future__ import annotations
from ..contrast import ColorContrast
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class LstarContrast(ColorContrast):
    """L* contrast."""

    NAME = "lstar"

    def contrast(self, color1: Color, color2: Color, **kwargs: Any) -> float:
        """Contrast."""

        l1 = color1.get('lch-d65.lightness', nans=False)
        l2 = color2.get('lch-d65.lightness', nans=False)

        if l1 > l2:
            l2, l1 = l1, l2

        return l2 - l1
