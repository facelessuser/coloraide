"""
Delta E 99o.

https://de.wikipedia.org/wiki/DIN99-Farbraum
"""
from __future__ import annotations
from ..distance import DeltaE, distance_euclidean
from ..types import AnyColor
from typing import Any


class DE99o(DeltaE):
    """Delta E 99o class."""

    NAME = '99o'

    def distance(self, color: AnyColor, sample: AnyColor, **kwargs: Any) -> float:
        """Get delta E 99o."""

        return distance_euclidean(color, sample, space='din99o')
