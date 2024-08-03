"""Distance and Delta E."""
from __future__ import annotations
import math
from .. import algebra as alg
from abc import ABCMeta, abstractmethod
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
        raise ValueError(f"'{method}' is not currently a supported distancing algorithm.")

    lowest = math.inf
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

    # convert to the specified space
    c1 = color.convert(space, norm=False)
    c2 = sample.convert(space, norm=False)
    coords1 = c1.coords(nans=False)
    coords2 = c2.coords(nans=False)

    # Convert polar coordinate into rectangular coordinates
    if c1._space.is_polar():
        hi = c1._space.hue_index()  # type: ignore[attr-defined]
        ri = c1._space.radial_index()  # type: ignore[attr-defined]
        a, b = alg.polar_to_rect(coords1[ri], coords1[hi])
        coords1[hi] = a
        coords1[ri] = b
        a, b = alg.polar_to_rect(coords2[ri], coords2[hi])
        coords2[hi] = a
        coords2[ri] = b

    return math.sqrt(sum((x - y) ** 2.0 for x, y in zip(coords1, coords2)))


class DeltaE(Plugin, metaclass=ABCMeta):
    """Delta E plugin class."""

    NAME = ''

    @abstractmethod
    def distance(self, color: Color, sample: Color, **kwargs: Any) -> float:
        """Get distance between color and sample."""
