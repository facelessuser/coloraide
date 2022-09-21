"""Delta E 76."""
from __future__ import annotations
from ..distance import DeltaE, distance_euclidean
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DE76(DeltaE):
    """Delta E 76 class."""

    NAME = "76"
    SPACE = "lab-d65"

    def distance(self, color: Color, sample: Color, **kwargs: Any) -> float:
        """
        Delta E 1976 color distance formula.

        http://www.brucelindbloom.com/index.html?Eqn_DeltaE_CIE76.html

        Basically this is Euclidean distance in the Lab space.
        """

        # Equation (1)
        return distance_euclidean(color, sample, space=self.SPACE)
