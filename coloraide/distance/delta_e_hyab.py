"""HyAB distance."""
from __future__ import annotations
from ..distance import DeltaE
import math
from ..spaces import Labish
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DEHyAB(DeltaE):
    """Delta E HyAB class."""

    NAME = "hyab"

    def __init__(self, space: str = "lab-d65") -> None:
        """Initialize."""

        self.space = space

    def distance(self, color: Color, sample: Color, space: str | None = None, **kwargs: Any) -> float:
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

        i = color._space.labish_indexes()
        coords1 = color.coords(nans=False)
        coords2 = sample.coords(nans=False)

        return (
            abs(coords1[i[0]] - coords2[i[0]]) +
            math.sqrt((coords1[i[1]] - coords2[i[1]]) ** 2 + (coords1[i[2]] - coords2[i[2]]) ** 2)
        )
