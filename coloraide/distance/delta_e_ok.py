"""Delta E OK."""
from ..distance import DeltaE, distance_euclidean
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DEOK(DeltaE):
    """Delta E OK class."""

    NAME = "ok"

    @staticmethod
    def distance(color: 'Color', sample: 'Color', scalar: float = 1, **kwargs: Any) -> float:
        """
        Delta E OK color distance formula.

        This just uses simple Euclidean distance in the Oklab color space.
        """

        # Equation (1)
        return scalar * distance_euclidean(color, sample, space="oklab")
