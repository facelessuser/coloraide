"""Delta E CAM16."""
from __future__ import annotations
import math
from ..distance import DeltaE
from ..spaces.cam16_ucs import COEFFICENTS
from ..types import VectorLike
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

COEFF2 = COEFFICENTS['ucs'][2]


def convert_ucs_ab(color: Color) -> VectorLike:
    """Convert HCT chroma and hue (CAM16 JMh colorfulness and hue) using UCS logic for a and b."""

    env = color._space.ENV  # type: ignore[attr-defined]
    h, c, t = color.coords()

    # Only in extreme cases (far outside the visible spectrum)
    # can the input value for log become negative.
    # Avoid domain error by forcing zero.
    M = math.log(max(1 + COEFF2 * c * env.fl_root, 1.0)) / COEFF2
    hrad = math.radians(h)
    a = M * math.cos(hrad)
    b = M * math.sin(hrad)

    return t, a, b


class DEHCT(DeltaE):
    """Delta E HCT class."""

    NAME = "hct"

    def distance(self, color: Color, sample: Color, **kwargs: Any) -> float:
        """Delta E HCT color distance formula."""

        t1, a1, b1 = convert_ucs_ab(
            color.convert('hct', norm=False) if color.space() != 'hct' else color.clone().normalize(nans=False)
        )
        t2, a2, b2 = convert_ucs_ab(
            sample.convert('hct', norm=False) if sample.space() != 'hct' else sample.clone().normalize(nans=False)
        )

        # Use simple euclidean distance
        return math.sqrt((t1 - t2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)
