"""
Delta E 99o.

https://de.wikipedia.org/wiki/DIN99-Farbraum
"""
from ..distance import DeltaE, distance_euclidean
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DE99o(DeltaE):
    """Delta E 99o class."""

    NAME = "99o"

    @staticmethod
    def distance(color: 'Color', sample: 'Color', **kwargs: Any) -> float:
        """Delta E 99o color distance formula."""

        # Equation (1)
        return distance_euclidean(color, sample, space="din99o")
