"""Delta E CAM16."""
from __future__ import annotations
import math
from ..distance import DeltaE
from ..spaces.cam16_ucs import COEFFICENTS
from ..types import Vector
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

COEFF2 = COEFFICENTS['ucs'][2]


def convert_ucs_ab(c: float, h: float) -> Vector:
    """Convert HCT chroma and hue (CAM16 JMh colorfulness and hue) to UCS a and b."""

    hrad = math.radians(h)
    M = math.log(1 + COEFF2 * c) / COEFF2
    a = M * math.cos(hrad)
    b = M * math.sin(hrad)

    return [a, b]


class DEHCT(DeltaE):
    """Delta E HCT class."""

    NAME = "hct"

    def distance(self, color: Color, sample: Color, **kwargs: Any) -> float:
        """Delta E HCT color distance formula."""

        h1, c1, t1 = color.convert('hct', norm=False).coords(nans=False)
        h2, c2, t2 = sample.convert('hct', norm=False).coords(nans=False)

        a1, b1 = convert_ucs_ab(c1, h1)
        a2, b2 = convert_ucs_ab(c2, h2)

        # Use simple euclidean distance
        return math.sqrt((t1 - t2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)
