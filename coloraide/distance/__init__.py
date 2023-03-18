"""Distance and Delta E."""
from __future__ import annotations
from abc import ABCMeta, abstractmethod
import math
from .. import algebra as alg
from ..types import ColorInput, Plugin
from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def closest(color: Color, colors: Sequence[ColorInput], method: str | None = None, **kwargs: Any) -> Color:
    """Get the closest color."""

    if method is None:
        method = color.DELTA_E

    algorithm = color.DE_MAP.get(method)
    if not algorithm:
        raise ValueError("'{}' is not currently a supported distancing algorithm.".format(method))

    lowest = alg.INF
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


def distance_euclidean(color: Color, sample: Color, space: str = "lab-d65") -> float:
    """
    Euclidean distance.

    https://en.wikipedia.org/wiki/Euclidean_distance
    """

    coords1 = color.convert(space, norm=False).coords(nans=False)
    coords2 = sample.convert(space, norm=False).coords(nans=False)

    return math.sqrt(sum((x - y) ** 2.0 for x, y in zip(coords1, coords2)))


class DeltaE(Plugin, metaclass=ABCMeta):
    """Delta E plugin class."""

    NAME = ''

    @abstractmethod
    def distance(self, color: Color, sample: Color, **kwargs: Any) -> float:
        """Get distance between color and sample."""
