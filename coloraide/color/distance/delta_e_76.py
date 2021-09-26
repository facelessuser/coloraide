"""Delta E 76."""
from ..distance import DeltaE
from . import distance_euclidean


class DE76(DeltaE):
    """Delta E 76 class."""

    @staticmethod
    def name():
        """Name of method."""

        return "76"

    @staticmethod
    def distance(color, sample, **kwargs):
        """
        Delta E 1976 color distance formula.

        http://www.brucelindbloom.com/index.html?Eqn_DeltaE_CIE76.html

        Basically this is Euclidean distance in the Lab space.
        """

        # Equation (1)
        return distance_euclidean.distance(color, sample, space="lab")
