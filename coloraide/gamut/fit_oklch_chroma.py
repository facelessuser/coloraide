"""Fit by compressing chroma in Oklch."""
from ..gamut import Fit, clip_channels
from ..util import NaN
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class OklchChroma(Fit):
    """Lch chroma gamut mapping class."""

    NAME = "oklch-chroma"

    EPSILON = 0.0001
    LIMIT = 0.02
    DE = "ok"
    SPACE = "oklch"
    MIN_LIGHTNESS = 0
    MAX_LIGHTNESS = 1

    @classmethod
    def fit(cls, color: 'Color', **kwargs: Any) -> None:
        """
        Algorithm originally came from https://colorjs.io/docs/gamut-mapping.html.

        Some things have been optimized and fixed though to better perform as intended.

        Algorithm basically uses a combination of chroma compression which helps to keep hue constant
        and color distancing to clip the color with minimal changes to other channels.

        We do not use the algorithm as defined in the CSS specification: https://drafts.csswg.org/css-color/#binsearch.
        This is because the current algorithm, as defined, has some issues that create gradients that are not smooth.

        ---
        Original Authors: Lea Verou, Chris Lilley
        License: MIT (As noted in https://github.com/LeaVerou/color.js/blob/master/package.json).
        """

        # Convert to CIELCH and set our boundaries
        mapcolor = color.convert(cls.SPACE)

        # Return white or black if lightness is out of range
        lightness = mapcolor.lightness
        if lightness >= cls.MAX_LIGHTNESS or lightness <= cls.MIN_LIGHTNESS:
            mapcolor.chroma = 0
            mapcolor.hue = NaN
            clip_channels(color.update(mapcolor))
            return

        low = 0.0
        high = mapcolor.chroma
        clip_channels(color.update(mapcolor))

        # If we are really close, skip gamut mapping and return the clipped value.
        if mapcolor.delta_e(color, method=cls.DE) >= cls.LIMIT:
            # Adjust chroma (using binary search).
            # This helps preserve the other attributes of the color.
            # Each time we compare the compressed color to it's clipped form
            # to see how close we are. A delta less than JND is our lower bound
            # and a value higher our upper. Continue until bounds converge.
            while (high - low) > cls.EPSILON:
                if mapcolor.delta_e(color, method=cls.DE) < cls.LIMIT:
                    low = mapcolor.chroma
                else:
                    high = mapcolor.chroma

                mapcolor.chroma = (high + low) * 0.5
                clip_channels(color.update(mapcolor))
