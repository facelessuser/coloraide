"""Fit by compressing chroma in Lch."""
from ..gamut import Fit, clip_channels
from ..util import NaN
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class LchChroma(Fit):
    """
    Lch chroma gamut mapping class.

    Adjust chroma (using binary search).
    This helps preserve the other attributes of the color.
    Compress chroma until we are are right at the JND edge while still out of gamut.
    Raise the lower chroma bound while we are in gamut or outside of gamut but still under the JND.
    Lower the upper chroma bound anytime we are out of gamut and above the JND.
    Too far under the JND we'll reduce chroma too aggressively.

    This is a compromise between the CSS algorithm as described in: https://www.w3.org/TR/css-color-4/#binsearch
    and what is used in https://github.com/LeaVerou/color.js. It optimizes the use of delta E calls to get somewhere
    in between CSS algorithm performance and the Color.js performance, but gets pretty close to the better chroma
    reduction.

    ---

    Based on the algorithm from from https://colorjs.io/docs/gamut-mapping.html.
    Original Authors: Lea Verou, Chris Lilley
    License: MIT (As noted in https://github.com/LeaVerou/color.js/blob/master/package.json).
    """

    NAME = "lch-chroma"

    EPSILON = 0.1
    LIMIT = 2.0
    DE = "2000"
    SPACE = "lch"
    MIN_LIGHTNESS = 0
    MAX_LIGHTNESS = 100

    @classmethod
    def fit(cls, color: 'Color', **kwargs: Any) -> None:
        """Gamut mapping via CIELCH chroma."""

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

        # Adjust chroma if we are not under the JND yet.
        if mapcolor.delta_e(color, method=cls.DE) >= cls.LIMIT:
            # Perform "in gamut" checks until we know our lower bound is no longer in gamut.
            lower_in_gamut = True

            while True:
                mapcolor.chroma = (high + low) * 0.5

                # Avoid doing expensive delta E checks if in gamut
                if lower_in_gamut and mapcolor.in_gamut(space, tolerance=0):
                    low = mapcolor.chroma
                else:
                    clip_channels(color.update(mapcolor))
                    de = mapcolor.delta_e(color, method=cls.DE)
                    if de < cls.LIMIT:
                        # Kick out as soon as we are close enough to the JND.
                        # Too far below and we may reduce chroma too aggressively.
                        if (cls.LIMIT - de) < cls.EPSILON:
                            break

                        # Our lower bound is now out of gamut, so all future searches are
                        # guaranteed to be out of gamut. Now we just want to focus on tuning
                        # chroma to get as close to the JND as possible.
                        if lower_in_gamut:
                            lower_in_gamut = False
                        low = mapcolor.chroma
                    else:
                        # We are still outside the gamut and outside the JND
                        high = mapcolor.chroma
