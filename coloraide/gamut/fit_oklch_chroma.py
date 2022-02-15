"""Fit by compressing chroma in Oklch."""
from ..gamut import Fit
from ..util import MutableVector, NaN
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
    SPACE_COORDINATE = "{}.chroma".format(SPACE)
    MIN_LIGHTNESS = 0
    MAX_LIGHTNESS = 1

    @classmethod
    def fit(cls, color: 'Color', **kwargs: Any) -> MutableVector:
        """
        Gamut mapping via Oklch chroma.

        Algorithm based on https://www.w3.org/TR/css-color-4/#binsearch.

        One difference is that we omit the step that clips the color and compares the
        clipped color to the chroma compressed color. Instead, we allow the low and high
        chroma bounds to converge. While diffing the clipped color with the chroma compressed
        color is marginally faster, occasionally you will get worse mappings, not hugely worse,
        but at times noticeable to decent eyes. We currently eat the minimal performance decrease
        to provide better mappings.
        """

        space = color.space()
        mapcolor = color.convert(cls.SPACE)
        lightness = mapcolor.lightness

        # If we are really close (in gamut with tolerance), skip gamut mapping and just clip
        if mapcolor.in_gamut(space):
            return color.clip(in_place=True).coords()

        # Return white or black if lightness is out of range
        if lightness >= cls.MAX_LIGHTNESS or lightness <= cls.MIN_LIGHTNESS:
            mapcolor.chroma = 0
            mapcolor.hue = NaN
            return color.update(mapcolor).clip(in_place=True).coords()

        # Set initial chroma boundaries
        low = 0.0
        high = mapcolor.chroma

        # Adjust chroma (using binary search).
        # This helps preserve the other attributes of the color.
        # Compress chroma until we are are right on the edge of being in gamut.
        while (high - low) > cls.EPSILON:
            if mapcolor.in_gamut(space, tolerance=0):
                low = mapcolor.chroma
            else:
                # CSS level 4 suggests comparing the chroma compressed color to the
                # clipped color here with delta E `ok` and kicking out if below the JND,
                # but the gained performance is small and the mapped color, in some
                # cases, can be a bit more off, at times even noticeable.
                # ```
                # color.update(mapcolor).clip(in_place=True)
                # if mapcolor.delta_e(color, method=cls.DE) < cls.LIMIT:
                #     break
                # ```
                high = mapcolor.chroma

            mapcolor.chroma = (high + low) * 0.5

        # Update and clip off noise
        return color.update(mapcolor).clip(in_place=True).coords()
