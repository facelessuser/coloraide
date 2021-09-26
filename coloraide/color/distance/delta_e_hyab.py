"""HyAB distance."""
from ..distance import DeltaE
import math
from ... import util
from ...spaces import Labish


class DEHyAB(DeltaE):
    """Delta E HyAB class."""

    @staticmethod
    def name():
        """Name of method."""

        return "hyab"

    @staticmethod
    def distance(color, sample, space="lab", **kwargs):
        """
        HyAB distance for Lab-ish spaces.

        http://markfairchild.org/PDFs/PAP40.pdf.
        """

        color = color.convert(space)
        sample = sample.convert(space)

        if not isinstance(color._space, Labish):
            raise ValueError("The space '{}' is not a 'lab-sh' color space and cannot use HyAB".format(space))

        names = color._space.labish_names()
        l1, a1, b1 = util.no_nan([color.get(names[0]), color.get(names[1]), color.get(names[2])])
        l2, a2, b2 = util.no_nan([sample.get(names[0]), sample.get(names[1]), sample.get(names[2])])

        return abs(l1 - l2) + math.sqrt((a1 - a2) ** 2 + (b1 - b2) ** 2)
