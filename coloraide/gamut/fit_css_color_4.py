"""CSS Color Level 4 gamut mapping."""
from ..gamut import Fit, clip_channels
from ..util import NaN
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class CssColor4(Fit):
    """Uses the CSS Color Level 4 algorithm for gamut mapping: Oklch: https://www.w3.org/TR/css-color-4/#binsearch."""

    NAME = "css-color-4"
    LIMIT = 0.02
    DE = "ok"
    SPACE = "oklch"
    MIN_LIGHTNESS = 0
    MAX_LIGHTNESS = 100

    @classmethod
    def fit(cls, color: 'Color', **kwargs: Any) -> None:
        """Gamut mapping via Oklch chroma."""

        space = color.space()
        mapcolor = color.convert(cls.SPACE)
        lightness = mapcolor.lightness

        # Return white or black if lightness is out of range
        if lightness >= cls.MAX_LIGHTNESS or lightness <= cls.MIN_LIGHTNESS:
            mapcolor.chroma = 0
            mapcolor.hue = NaN
            clip_channels(color.update(mapcolor))
            return

        # Set initial chroma boundaries
        low = 0.0
        high = mapcolor.chroma
        clip_channels(color.update(mapcolor))

        # Adjust chroma (using binary search).
        # This helps preserve the other attributes of the color.
        # Compress chroma until we are are right outside the gamut, but under the JND.
        if not mapcolor.in_gamut(space):
            while True:
                mapcolor.chroma = (high + low) * 0.5

                if mapcolor.in_gamut(space, tolerance=0):
                    low = mapcolor.chroma
                else:
                    clip_channels(color.update(mapcolor))
                    if mapcolor.delta_e(color, method=cls.DE) < cls.LIMIT:
                        break
                    high = mapcolor.chroma
