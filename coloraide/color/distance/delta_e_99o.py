"""
Delta E 99o.

https://de.wikipedia.org/wiki/DIN99-Farbraum
"""
from . import distance_euclidean
import math
from ... import util


def distance(color, sample, **kwargs):
    """Delta E ITP color distance formula."""

    # Equation (1)
    return distance_euclidean.distance(color1, color2, space="din99o-lab")
