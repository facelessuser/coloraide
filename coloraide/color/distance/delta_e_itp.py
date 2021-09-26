"""
Delta E ITP.

https://kb.portrait.com/help/ictcp-color-difference-metric
"""
from ..distance import DeltaE
import math
from ... import util


class DEITP(DeltaE):
    """Delta E ITP class."""

    @staticmethod
    def name():
        """Name of method."""

        return "itp"

    @staticmethod
    def distance(color, sample, scalar=720, **kwargs):
        """Delta E ITP color distance formula."""

        i1, t1, p1 = util.no_nan(color.convert('ictcp').coords())
        i2, t2, p2 = util.no_nan(sample.convert('ictcp').coords())

        # Equation (1)
        return scalar * math.sqrt((i1 - i2) ** 2 + 0.25 * (t1 - t2) ** 2 + (p1 - p2) ** 2)
