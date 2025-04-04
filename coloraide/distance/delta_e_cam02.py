"""
Delta E CAM02.

https://en.wikipedia.org/wiki/CIECAM02
https://www.researchgate.net/publication/221501922_The_CIECAM02_color_appearance_model

The articles don't specifically cover the distancing algorithm, but CAM02 uses the same
UCS code and applies the same distancing algorithm as CAM16.

https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9698626/pdf/sensors-22-08869.pdf
"""
from __future__ import annotations
import math
from ..distance import DeltaE
from ..spaces.cam02_ucs import CAM02UCS
from ..spaces.cam16_ucs import COEFFICENTS
from ..types import AnyColor
from typing import Any


class DECAM02(DeltaE):
    """Delta E CAM02 class."""

    NAME = "cam02"

    def distance(
        self,
        color: AnyColor,
        sample: AnyColor,
        space: str = "cam02-ucs",
        **kwargs: Any
    ) -> float:
        """Delta E CAM02 color distance formula."""

        # Normal approach to specifying CAM02 target space
        cs = color.CS_MAP[space]
        if not isinstance(color.CS_MAP[space], CAM02UCS):
            raise ValueError("Distance color space must be derived from CAM02UCS.")
        model = cs.MODEL  # type: ignore[attr-defined]
        kl = COEFFICENTS[model][0]

        j1, a1, b1 = color.convert(space).coords(nans=False)
        j2, a2, b2 = sample.convert(space).coords(nans=False)

        dj = j1 - j2
        da = a1 - a2
        db = b1 - b2

        return math.sqrt((dj / kl) ** 2 + da ** 2 + db ** 2)
