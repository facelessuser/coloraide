"""
Delta E CAM16.

https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9698626/pdf/sensors-22-08869.pdf
"""
from __future__ import annotations
import math
from ..distance import DeltaE
from .. import algebra as alg
from typing import Any, TYPE_CHECKING
from ..spaces.cam16_ucs import COEFFICENTS

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DECAM16(DeltaE):
    """Delta E CAM16 class."""

    NAME = "cam16"

    def distance(self, color: Color, sample: Color, model: str = 'ucs', **kwargs: Any) -> float:
        """Delta E z color distance formula."""

        space = 'cam16-{}'.format(model)
        kl = COEFFICENTS[model][0]
        j1, a1, b1 = alg.no_nans(color.convert(space)[:-1])
        j2, a2, b2 = alg.no_nans(sample.convert(space)[:-1])

        dj = j1 - j2
        da = a1 - a2
        db = b1 - b2

        return math.sqrt((dj / kl) ** 2 + da ** 2 + db ** 2)
