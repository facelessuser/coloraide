"""Fit by compressing chroma in LCh."""
from __future__ import annotations
from ..gamut import Fit, clip_channels
from ..cat import WHITES
from .. import util
import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

WHITE = util.xy_to_xyz(WHITES['2deg']['D65'])
BLACK = [0, 0, 0]


class LChChroma(Fit):
    """
    LCh chroma gamut mapping class.

    Adjust chroma (using binary search).
    This helps preserve the other attributes of the color.
    Compress chroma until we are are right at the JND edge while still out of gamut.
    Raise the lower chroma bound while we are in gamut or outside of gamut but still under the JND.
    Lower the upper chroma bound anytime we are out of gamut and above the JND.
    Too far under the JND we'll reduce chroma too aggressively.

    This is the same as the CSS algorithm as described here: https://www.w3.org/TR/css-color-4/#binsearch.
    There are some small adjustments to handle HDR colors as the CSS algorithm assumes SDR color spaces.
    Additionally, this uses LCh instead of OkLCh, but we also offer a derived version that uses OkLCh.
    """

    NAME = "lch-chroma"

    EPSILON = 0.1
    LIMIT = 2.0
    DE = "2000"
    DE_OPTIONS = {}  # type: dict[str, Any]
    SPACE = "lch-d65"
    MIN_LIGHTNESS = 0
    MAX_LIGHTNESS = 100
    MIN_CONVERGENCE = 0.0001

    def fit(self, color: Color, **kwargs: Any) -> None:
        """Gamut mapping via CIELCh chroma."""

        space = color.space()
        mapcolor = color.convert(self.SPACE, norm=False)
        l, c = mapcolor._space.indexes()[:2]  # type: ignore[attr-defined]
        lightness = mapcolor[l]
        sdr = color._space.DYNAMIC_RANGE == 'sdr'

        # Return white or black if lightness is out of dynamic range for lightness.
        # Extreme light case only applies to SDR, but dark case applies to all ranges.
        if sdr and (lightness >= self.MAX_LIGHTNESS or math.isclose(lightness, self.MAX_LIGHTNESS, abs_tol=1e-6)):
            clip_channels(color.update('xyz-d65', WHITE, mapcolor[-1]))
            return
        elif lightness <= self.MIN_LIGHTNESS:
            clip_channels(color.update('xyz-d65', BLACK, mapcolor[-1]))
            return

        # Set initial chroma boundaries
        low = 0.0
        high = mapcolor[c]
        clip_channels(color._hotswap(mapcolor.convert(space, norm=False)))

        # Adjust chroma if we are not under the JND yet.
        if mapcolor.delta_e(color, method=self.DE, **self.DE_OPTIONS) >= self.LIMIT:
            # Perform "in gamut" checks until we know our lower bound is no longer in gamut.
            lower_in_gamut = True

            # If high and low get too close to converging,
            # we need to quit in order to prevent infinite looping.
            while (high - low) > self.MIN_CONVERGENCE:
                mapcolor[c] = (high + low) * 0.5

                # Avoid doing expensive delta E checks if in gamut
                if lower_in_gamut and mapcolor.in_gamut(space, tolerance=0):
                    low = mapcolor[c]
                else:
                    clip_channels(color._hotswap(mapcolor.convert(space, norm=False)))
                    de = mapcolor.delta_e(color, method=self.DE, **self.DE_OPTIONS)
                    if de < self.LIMIT:
                        # Kick out as soon as we are close enough to the JND.
                        # Too far below and we may reduce chroma too aggressively.
                        if (self.LIMIT - de) < self.EPSILON:
                            break

                        # Our lower bound is now out of gamut, so all future searches are
                        # guaranteed to be out of gamut. Now we just want to focus on tuning
                        # chroma to get as close to the JND as possible.
                        if lower_in_gamut:
                            lower_in_gamut = False
                        low = mapcolor[c]
                    else:
                        # We are still outside the gamut and outside the JND
                        high = mapcolor[c]
        color.normalize()
