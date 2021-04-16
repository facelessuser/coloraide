"""Euclidean distance."""
import math
from ... import util


def distance(color1, color2, space="lab", **kwargs):
    """
    Euclidean distance.

    https://en.wikipedia.org/wiki/Euclidean_distance
    """

    coords1 = util.no_nan(color1.convert(space).coords())
    coords2 = util.no_nan(color2.convert(space).coords())

    return math.sqrt(sum((x - y) ** 2.0 for x, y in zip(coords2, coords1)))
