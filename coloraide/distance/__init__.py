"""Distance and Delta E."""
from abc import ABCMeta, abstractmethod
from .. import util
import math
from ..util import ColorInput
from typing import TYPE_CHECKING, Any, Sequence, Optional

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def closest(color: 'Color', colors: Sequence[ColorInput], method: Optional[str] = None, **kwargs: Any) -> 'Color':
    """Get the closest color."""

    if method is None:
        method = color.DELTA_E

    try:
        algorithm = color.DE_MAP[method]
    except KeyError:
        raise ValueError("'{}' is not currently a supported distancing algorithm.".format(method))

    lowest = float('inf')
    closest = None
    for c in colors:
        color2 = color._handle_color_input(c)
        de = algorithm.distance(color, color2, **kwargs)
        if de < lowest:
            lowest = de
            closest = color2

    if closest is None:
        raise ValueError('No colors to compare')

    return closest


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
