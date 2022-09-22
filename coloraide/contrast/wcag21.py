"""
WCAG 2.1 contrast ratio.

https://www.w3.org/TR/WCAG20/#contrast-ratiodef
"""
from __future__ import annotations
from ..contrast import ColorContrast
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class WCAG21Contrast(ColorContrast):
    """WCAG 2.1 contrast ratio."""

    NAME = "wcag21"

    def contrast(self, color1: Color, color2: Color, **kwargs: Any) -> float:
        """Contrast."""

        lum1 = max(0, color1.luminance())
        lum2 = max(0, color2.luminance())
        if (lum1 > lum2):
            lum1, lum2 = lum2, lum1
        return (lum2 + 0.05) / (lum1 + 0.05)
