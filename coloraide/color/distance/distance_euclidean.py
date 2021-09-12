"""Euclidean distance."""
import math
from ... import util


def distance(color, sample, space="lab", **kwargs):
    """
    Euclidean distance.

    https://en.wikipedia.org/wiki/Euclidean_distance
    """

    coords1 = util.no_nan(color.convert(space).coords())
    coords2 = util.no_nan(sample.convert(space).coords())

    return math.sqrt(sum((x - y) ** 2.0 for x, y in zip(coords1, coords2)))
