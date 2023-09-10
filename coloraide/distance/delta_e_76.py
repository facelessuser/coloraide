"""Delta E 76."""
from __future__ import annotations
from ..distance import DeltaE, distance_euclidean
from typing import TYPE_CHECKING, Any
from ..spaces.lab import CIELab
if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DE76(DeltaE):
    """Delta E 76 class."""

    NAME = "76"

    def __init__(self, space: str = 'lab-d65'):
        """Initialize."""

        self.space = space

    def distance(
        self,
        color: Color,
        sample: Color,
        space: str | None = None,
        **kwargs: Any
    ) -> float:
        """
        Delta E 1976 color distance formula.

        http://www.brucelindbloom.com/index.html?Eqn_DeltaE_CIE76.html

        Basically this is Euclidean distance in the Lab space.
        """

        if space is None:
            space = self.space
        if not isinstance(color.CS_MAP[space], CIELab):
            raise ValueError("Distance color space must be a CIE Lab color space.")

        # Equation (1)
        return distance_euclidean(color, sample, space=space)
