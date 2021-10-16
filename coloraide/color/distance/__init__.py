"""Distance and Delta E."""
from abc import ABCMeta, abstractmethod
from ... import util
import math


def distance_euclidean(color, sample, space="lab"):
    """
    Euclidean distance.

    https://en.wikipedia.org/wiki/Euclidean_distance
    """

    coords1 = util.no_nan(color.convert(space).coords())
    coords2 = util.no_nan(sample.convert(space).coords())

    return math.sqrt(sum((x - y) ** 2.0 for x, y in zip(coords1, coords2)))


class DeltaE(ABCMeta):
    """Delta E plugin class."""

    @staticmethod
    @abstractmethod
    def name():
        """Get name of method."""

    @staticmethod
    @abstractmethod
    def distance(color, sample, **kwargs):
        """Get distance between color and sample."""


class Distance:
    """Distance."""

    def delta_e(self, color, *, method=None, **kwargs):
        """Delta E distance."""

        color = self._handle_color_input(color)
        if method is None:
            method = self.DELTA_E

        algorithm = method.lower()

        try:
            return self.DE_MAP[algorithm](self, color, **kwargs)
        except KeyError:
            raise ValueError("'{}' is not currently a supported distancing algorithm.".format(algorithm))

    def distance(self, color, *, space="lab"):
        """Delta."""

        color = self._handle_color_input(color)
        return distance_euclidean(self, color, space=space)
