"""HyAB distance."""
from __future__ import annotations
from ..distance import DeltaE
import math
from .. import algebra as alg
from ..spaces import Labish
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DEHyAB(DeltaE):
    """Delta E HyAB class."""

    NAME = "hyab"

    def __init__(self, space: str = "lab-d65") -> None:
        """Initialize."""

        self.space = space

    def distance(self, color: Color, sample: Color, space: Optional[str] = None, **kwargs: Any) -> float:
        """
        HyAB distance for Lab-ish spaces.

        http://markfairchild.org/PDFs/PAP40.pdf.
        """

        if space is None:
            space = self.space

        color = color.convert(space)
        sample = sample.convert(space)

        if not isinstance(color._space, Labish):
            raise ValueError("The space '{}' is not a 'lab-ish' color space and cannot use HyAB".format(space))

        names = color._space.labish_names()
        l1, a1, b1 = alg.no_nans(color.get(names))
        l2, a2, b2 = alg.no_nans(sample.get(names))

        return abs(l1 - l2) + math.sqrt((a1 - a2) ** 2 + (b1 - b2) ** 2)
