"""Distance and Delta E."""
from abc import ABCMeta, abstractmethod
from .. import util
import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def distance_euclidean(color: 'Color', sample: 'Color', space: str = "lab") -> float:
    """
    Euclidean distance.

    https://en.wikipedia.org/wiki/Euclidean_distance
    """

    coords1 = util.no_nans(color.convert(space).coords())
    coords2 = util.no_nans(sample.convert(space).coords())

    return math.sqrt(sum((x - y) ** 2.0 for x, y in zip(coords1, coords2)))


class DeltaE(ABCMeta):
    """Delta E plugin class."""

    NAME = ''

    @classmethod
    @abstractmethod
    def distance(cls, color: 'Color', sample: 'Color', **kwargs: Any) -> float:
        """Get distance between color and sample."""
