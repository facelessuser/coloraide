"""HyAB distance."""
from ..distance import DeltaE
import math
from .. import util
from ..spaces import Labish
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DEHyAB(DeltaE):
    """Delta E HyAB class."""

    NAME = "hyab"

    @classmethod
    def distance(cls, color: 'Color', sample: 'Color', space: str = "lab", **kwargs: Any) -> float:
        """
        HyAB distance for Lab-ish spaces.

        http://markfairchild.org/PDFs/PAP40.pdf.
        """

        color = color.convert(space)
        sample = sample.convert(space)

        if not isinstance(color._space, Labish):
            raise ValueError("The space '{}' is not a 'lab-sh' color space and cannot use HyAB".format(space))

        names = color._space.labish_names()
        l1, a1, b1 = util.no_nans([color.get(names[0]), color.get(names[1]), color.get(names[2])])
        l2, a2, b2 = util.no_nans([sample.get(names[0]), sample.get(names[1]), sample.get(names[2])])

        return abs(l1 - l2) + math.sqrt((a1 - a2) ** 2 + (b1 - b2) ** 2)
