"""Delta E OK."""
from .delta_e_76 import DE76
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class DEOK(DE76):
    """Delta E OK class."""

    NAME = "ok"
    SPACE = "oklab"

    @classmethod
    def distance(cls, color: 'Color', sample: 'Color', scalar: float = 1, **kwargs: Any) -> float:
        """
        Delta E OK color distance formula.

        This just uses simple Euclidean distance in the Oklab color space.
        """

        # Equation (1)
        return scalar * super().distance(color, sample)
