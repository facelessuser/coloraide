"""Delta E OK."""
from ..distance import DeltaE, distance_euclidean


class DEOK(DeltaE):
    """Delta E OK class."""

    @staticmethod
    def name():
        """Name of method."""

        return "ok"

    @staticmethod
    def distance(color, sample, scalar=1, **kwargs):
        """
        Delta E OK color distance formula.

        This just uses simple Euclidean distance in the Oklab color space.
        """

        # Equation (1)
        return scalar * distance_euclidean(color, sample, space="oklab")
