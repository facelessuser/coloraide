"""
L* color contrast.

Used for color contrast in Google's HCT.

https://material.io/blog/science-of-color-design
"""
from __future__ import annotations
from ..contrast import ColorContrast
from ..types import AnyColor
from typing import Any


class LstarContrast(ColorContrast):
    """L* contrast."""

    NAME = "lstar"

    def contrast(self, color1: AnyColor, color2: AnyColor, **kwargs: Any) -> float:
        """Contrast."""

        l1 = color1.get('lch-d65.lightness', nans=False)
        l2 = color2.get('lch-d65.lightness', nans=False)

        if l1 > l2:
            l2, l1 = l1, l2

        return l2 - l1
