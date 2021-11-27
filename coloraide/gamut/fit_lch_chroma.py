"""Fit by compressing chroma in Lch."""
from ..gamut import Fit
from ..util import MutableVector
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class LchChroma(Fit):
    """Lch chroma gamut mapping class."""

    NAME = "lch-chroma"

    EPSILON = 0.01
    DE = "2000"
    SPACE = "lch"
    SPACE_COORDINATE = "{}.chroma".format(SPACE)
    LIMIT = 2.0

    @classmethod
    def fit(cls, color: 'Color') -> MutableVector:
        """
        Gamut mapping via chroma Lch.

        Algorithm originally came from https://colorjs.io/docs/gamut-mapping.html.
        Some things have been optimized and fixed though to better perform as intended.

        The idea is to hold hue and lightness constant and decrease chroma until
        color comes under gamut.

        We'll use a binary search and at after each stage, we will clip the color
        and compare the distance of the two colors (clipped and current color via binary search).
        If the distance is less than two, we can return the clipped color.

        ---
        Original Authors: Lea Verou, Chris Lilley
        License: MIT (As noted in https://github.com/LeaVerou/color.js/blob/master/package.json)
        """

        space = color.space()

        # If flooring chroma doesn't work, just clip the floored color
        # because there is no optimal compression.
        floor = color.clone().set(cls.SPACE_COORDINATE, 0)
        if not floor.in_gamut(tolerance=0):
            return floor.clip().coords()

        # If we are already below the JND, just clip as we will gain no
        # noticeable difference moving forward.
        clipped = color.clip()
        if color.delta_e(clipped, method=cls.DE) < cls.LIMIT:
            return clipped.coords()

        # Convert to CIELCH and set our boundaries
        mapcolor = color.convert(cls.SPACE)
        low = 0.0
        high = mapcolor.chroma

        # Adjust chroma (using binary search).
        # This helps preserve the other attributes of the color.
        # Each time we compare the compressed color to it's clipped form
        # to see how close we are. A delta less than 2 is our target.
        while (high - low) > cls.EPSILON:
            delta = mapcolor.delta_e(
                mapcolor.clip(space),
                method=cls.DE
            )

            if (delta - cls.LIMIT) < cls.EPSILON:
                low = mapcolor.chroma
            else:
                high = mapcolor.chroma

            mapcolor.chroma = (high + low) * 0.5

        # Update and clip off noise
        return color.update(mapcolor).clip(space, in_place=True).coords()
