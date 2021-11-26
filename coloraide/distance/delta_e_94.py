"""Delta E 94."""
from ..distance import DeltaE
import math
from .. import util
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DE94(DeltaE):
    """Delta E 94 class."""

    NAME = "94"

    @classmethod
    def distance(
        cls,
        color: 'Color',
        sample: 'Color',
        kl: float = 1,
        k1: float = 0.045,
        k2: float = 0.015,
        **kwargs: Any
    ) -> float:
        """
        Delta E 1994 color distance formula.

        http://www.brucelindbloom.com/Eqn_DeltaE_CIE94.html
        """

        l1, a1, b1 = util.no_nans(color.convert("lab").coords())
        l2, a2, b2 = util.no_nans(sample.convert("lab").coords())

        # Equation (5)
        c1 = math.sqrt(a1 ** 2 + b1 ** 2)

        # Equation (6)
        c2 = math.sqrt(a2 ** 2 + b2 ** 2)

        # Equation  (2)
        dl = l1 - l2

        # Equation  (3)
        dc = c1 - c2

        # Equation (7)
        da = a1 - a2

        # Equation  (8)
        db = b1 - b2

        # Equation (4)
        # We never reference `dh` until the very end, and when we do, we square it
        # before using it, so we don't need the square root as described in the
        # algorithm. Instead we can just leave the result as is.
        dh = da ** 2 + db ** 2 - dc ** 2

        # Equation (9)
        sl = 1

        # Equation (10)
        sc = 1 + k1 * c1

        # Equation (11)
        sh = 1 + k2 * c1

        # Equation (12)
        # Provided by `kl`

        # Equation (13)
        kc = 1

        # Equation (14)
        kh = 1

        # Equation (15) and Equation (16)
        # Provided by `k1` and `k2`

        # Equation (1)
        return math.sqrt(
            (dl / (kl * sl)) ** 2 +
            (dc / (kc * sc)) ** 2 +
            # Square root just the denominator as `dh` is already squared.
            dh / ((kh * sh) ** 2)
        )
