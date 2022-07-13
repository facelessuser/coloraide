"""
WCAG 2.1 contrast ratio.

https://www.w3.org/TR/WCAG20/#contrast-ratiodef
"""
from ..contrast import ColorContrast
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class WCAG21Contrast(ColorContrast):
    """WCAG 2.1 contrast ratio."""

    NAME = "wcag21"

    @classmethod
    def contrast(cls, color1: 'Color', color2: 'Color', **kwargs: Any) -> float:
        """Contrast."""

        lum1 = color1.luminance()
        lum2 = color2.luminance()
        return (lum1 + 0.05) / (lum2 + 0.05) if (lum1 > lum2) else (lum2 + 0.05) / (lum1 + 0.05)
