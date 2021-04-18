"""Delta E 76."""

from . import distance_euclidean


def distance(color1, color2, **kwargs):
    """
    Delta E 1976 color distance formula.

    http://www.brucelindbloom.com/index.html?Eqn_DeltaE_CIE76.html

    Basically this is Euclidean distance in the Lab space.
    """

    # Equation (1)
    return distance_euclidean.distance(color1, color2, space="lab")
