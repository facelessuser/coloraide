"""Delta E OK."""
from __future__ import annotations
from ..distance import DeltaE, distance_euclidean
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DEOK(DeltaE):
    """Delta E 99o class."""

    NAME = 'ok'

    def __init__(self, scalar: float = 1) -> None:
        """Initialize."""

        self.scalar = scalar

    def distance(self, color: Color, sample: Color, scalar: float | None = None, **kwargs: Any) -> float:
        """
        Delta E OK color distance formula.

        This just uses simple Euclidean distance in the Oklab color space.
        """

        if scalar is None:
            scalar = self.scalar

        return scalar * distance_euclidean(color, sample, space='oklab')
