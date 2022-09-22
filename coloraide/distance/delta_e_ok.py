"""Delta E OK."""
from __future__ import annotations
from .delta_e_76 import DE76
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DEOK(DE76):
    """Delta E OK class."""

    NAME = "ok"
    SPACE = "oklab"

    def __init__(self, scalar: float = 1) -> None:
        """Initialize."""

        self.scalar = scalar

    def distance(self, color: Color, sample: Color, scalar: Optional[float] = None, **kwargs: Any) -> float:
        """
        Delta E OK color distance formula.

        This just uses simple Euclidean distance in the Oklab color space.
        """

        if scalar is None:
            scalar = self.scalar

        # Equation (1)
        return scalar * super().distance(color, sample)
