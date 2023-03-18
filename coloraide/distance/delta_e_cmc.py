"""Delta E CMC."""
from __future__ import annotations
from ..distance import DeltaE
import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DECMC(DeltaE):
    """Delta E CMC class."""

    NAME = "cmc"

    def __init__(
        self,
        l: float = 2,
        c: float = 1
    ):
        """Initialize."""

        self.l = l
        self.c = c

    def distance(
        self,
        color: Color,
        sample: Color,
        l: float | None = None,
        c: float | None = None,
        **kwargs: Any
    ) -> float:
        """
        Delta E CMC.

        http://www.brucelindbloom.com/index.html?Eqn_DeltaE_CMC.html
        """

        if l is None:
            l = self.l

        if c is None:
            c = self.c

        l1, a1, b1 = color.convert("lab").coords(nans=False)
        l2, a2, b2 = sample.convert("lab").coords(nans=False)

        # Equation (3)
        c1 = math.sqrt(a1 ** 2 + b1 ** 2)

        # Equation (4)
        c2 = math.sqrt(a2 ** 2 + b2 ** 2)

        # Equation (2)
        dc = c1 - c2

        # Equation (6)
        dl = l1 - l2

        # Equation (7)
        da = a1 - a2

        # Equation (8)
        db = b1 - b2

        # Equation (5)
        # We never reference `dh` until the very end, and when we do, we square it
        # before using it, so we don't need the square root as described in the
        # algorithm. Instead we can just leave the result as is.
        dh = da ** 2 + db ** 2 - dc ** 2

        # Equation (9)
        if l1 < 16:
            sl = 0.511
        else:
            sl = (0.040975 * l1) / (1 + 0.01765 * l1)

        # Equation (10)
        sc = ((0.0638 * c1) / (1 + 0.0131 * c1)) + 0.638

        # Equation (14)
        h = math.degrees(math.atan2(b1, a1))

        # Equation (15)
        if h >= 0:
            h1 = h
        else:
            h1 = h + 360

        # Equation (12)
        if 164 <= h1 <= 345:
            t = 0.56 + abs(0.2 * math.cos(math.radians(h1 + 168)))
        else:
            t = 0.36 + abs(0.4 * math.cos(math.radians(h1 + 35)))

        # Equation (13)
        c1_4 = c1 ** 4
        f = math.sqrt(c1_4 / (c1_4 + 1900))

        # Equation (11)
        sh = sc * (f * t + 1 - f)

        # Equation (1)
        return math.sqrt(
            (dl / (l * sl)) ** 2 +
            (dc / (c * sc)) ** 2 +
            # Square root just the denominator as `dh` is already squared.
            dh / (sh ** 2)
        )
