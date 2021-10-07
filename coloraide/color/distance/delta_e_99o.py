"""
Delta E 99o.

https://de.wikipedia.org/wiki/DIN99-Farbraum
"""
from ..distance import DeltaE, distance_euclidean


class DE99o(DeltaE):
    """Delta E 99o class."""

    @staticmethod
    def name():
        """Name of method."""

        return "99o"

    @staticmethod
    def distance(color, sample, **kwargs):
        """Delta E 99o color distance formula."""

        # Equation (1)
        return distance_euclidean(color, sample, space="din99o")
