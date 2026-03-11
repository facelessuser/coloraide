"""
Delta E Helmlab.

- https://arxiv.org/abs/2602.23010
- https://github.com/Grkmyldz148/helmlab
"""
from __future__ import annotations
import math
from . import DeltaE
from ..types import AnyColor
from typing import Any

SL = 0.0010089809904916469
SC = 0.021678192255028452
WC = 1.0458243890301122
P = 0.804265429185275
COMPRESS = 1.5903206798028005
Q = 1.1


class DEHelmlab(DeltaE):
    """Delta E Helmlab class."""

    NAME = "helmlab"

    def distance(self, color: AnyColor, sample: AnyColor, **kwargs: Any) -> float:
        """Delta E Helmlab color distance formula."""

        l1, a1, b1 = (
            color.convert('helmlab') if color.space() != 'helmlab' else color.clone().normalize(nans=False)
        )[:-1]
        l2, a2, b2 = (
            sample.convert('helmlab') if color.space() != 'helmlab' else sample.clone().normalize(nans=False)
        )[:-1]

        dl = l1 - l2
        da = a1 - a2
        db = b1 - b2

        # Pair-dependent weighting
        lavg = (l1 + l2) * 0.5
        sl = 1 + SL * (lavg - 0.5) ** 2

        c1 = math.sqrt(a1 ** 2 + b1 ** 2)
        c2 = math.sqrt(a2 ** 2 + b2 ** 2)
        cavg = (c1 + c2) * 0.5
        sc = 1.0 + SC * cavg

        # Weighted Minkowski distance
        raw = (dl ** 2 / sl ** 2 + WC * (da ** 2 + db ** 2) / sc ** 2) ** (P / 2)

        # Monotonic compression
        compressed = raw / (1.0 + COMPRESS * raw)

        return compressed ** Q
