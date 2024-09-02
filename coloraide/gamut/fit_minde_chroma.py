"""Fit by compressing chroma in LCh."""
from __future__ import annotations
import functools
from ..gamut import Fit, clip_channels
from ..cat import WHITES
from .. import util
import math
from .. import algebra as alg
from .tools import adaptive_hue_independent
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

XYZ = 'xyz-d65'
WHITE = util.xy_to_xyz(WHITES['2deg']['D65'])
BLACK = [0.0, 0.0, 0.0]


@functools.lru_cache(maxsize=10)
def calc_epsilon(jnd: float) -> float:
    """Calculate the epsilon to 2 degrees smaller than the specified JND."""

    return float(f"1e{alg.order(jnd) - 2:d}")


class MINDEChroma(Fit):
    """
    Chroma reduction with MINDE.

    Adjust chroma (using binary search) which helps preserve perceptual hue and lightness.
    Compress chroma until we are right at the JND edge while still out of gamut.
    Raise the lower chroma bound while we are in gamut or outside of gamut but still under the JND.
    Lower the upper chroma bound anytime we are out of gamut and above the JND.
    Too far under the JND we'll reduce chroma too aggressively.

    This is the same as the CSS algorithm as described here: https://www.w3.org/TR/css-color-4/#binsearch.
    There are some small adjustments to handle HDR colors as the CSS algorithm assumes SDR color spaces.
    Additionally, this uses LCh instead of OkLCh, but we also offer a derived version that uses OkLCh.
    """

    NAME = "minde-chroma"
    JND = 0.02
    DE_OPTIONS = {"method": "ok"}  # type: dict[str, Any]
    PSPACE = "oklch"
    MIN_CONVERGENCE = 0.0001

    def fit(
        self,
        color: Color,
        space: str,
        *,
        pspace: str | None = None,
        jnd: float | None = None,
        de_options: dict[str, Any] | None = None,
        adaptive: float = 0.0,
        **kwargs: Any
    ) -> None:
        """Gamut mapping via CIELCh chroma."""

        # Identify the perceptual space and determine if it is rectangular or polar
        if pspace is None:
            pspace = self.PSPACE
        polar = color.CS_MAP[pspace].is_polar()
        orig = color.space()
        mapcolor = color.convert(pspace, norm=False) if orig != pspace else color.clone().normalize(nans=False)
        gamutcolor = color.convert(space, norm=False) if orig != space else color.clone().normalize(nans=False)
        if polar:
            l, c, h = mapcolor._space.indexes()  # type: ignore[attr-defined]
        else:
            l, a, b = mapcolor._space.indexes()  # type: ignore[attr-defined]
        lightness = mapcolor[l]
        sdr = gamutcolor._space.DYNAMIC_RANGE == 'sdr'
        if jnd is None:
            jnd = self.JND
        epsilon = calc_epsilon(jnd)

        if de_options is None:
            de_options = self.DE_OPTIONS

        temp = color.new(XYZ, WHITE, mapcolor[-1]).convert(pspace, in_place=True)
        max_light = temp[l]

        # Return white or black if lightness is out of dynamic range for lightness.
        # Extreme light case only applies to SDR, but dark case applies to all ranges.
        if not adaptive:
            if sdr and (lightness >= max_light or math.isclose(lightness, max_light, abs_tol=1e-6)):
                clip_channels(color.update(temp))
                return
            elif lightness <= temp.update(XYZ, BLACK, mapcolor[-1])[l]:
                clip_channels(color.update(temp))
                return

            low = 0.0
            high, hue = (mapcolor[c], mapcolor[h]) if polar else alg.rect_to_polar(mapcolor[a], mapcolor[b])
        else:
            chroma, hue = (mapcolor[c], mapcolor[h]) if polar else alg.rect_to_polar(mapcolor[a], mapcolor[b])
            light = mapcolor[l]
            alight = adaptive_hue_independent(light / max_light, max(chroma, 0.0) / max_light, adaptive) * max_light
            achroma = low = 0.0
            high = 1.0

        clip_channels(gamutcolor)

        # Adjust chroma if we are not under the JND yet.
        if not jnd or mapcolor.delta_e(gamutcolor, **de_options) >= jnd:
            # Perform "in gamut" checks until we know our lower bound is no longer in gamut.
            lower_in_gamut = True

            # If high and low get too close to converging,
            # we need to quit in order to prevent infinite looping.
            while (high - low) > self.MIN_CONVERGENCE:
                value = (high + low) * 0.5
                if not adaptive:
                    if polar:
                        mapcolor[c] = value
                    else:
                        mapcolor[a], mapcolor[b] = alg.polar_to_rect(value, hue)
                else:
                    mapcolor[l], c_ =  alg.lerp(alight, light, value), alg.lerp(achroma, chroma, value)
                    if polar:
                        mapcolor[c] = c_
                    else:
                        mapcolor[a], mapcolor[b] = alg.polar_to_rect(c_, hue)

                # Avoid doing expensive delta E checks if in gamut
                temp = mapcolor.convert(space, norm=False)
                if lower_in_gamut and temp.in_gamut(tolerance=0):
                    low = value
                else:
                    gamutcolor = temp
                    clip_channels(gamutcolor)
                    # Bypass distance check if JND is 0
                    de = mapcolor.delta_e(gamutcolor, **de_options) if jnd else 0.0
                    if de < jnd:
                        # Kick out as soon as we are close enough to the JND.
                        # Too far below and we may reduce chroma too aggressively.
                        if (jnd - de) < epsilon:
                            break

                        # Our lower bound is now out of gamut, so all future searches are
                        # guaranteed to be out of gamut. Now we just want to focus on tuning
                        # chroma to get as close to the JND as possible.
                        if lower_in_gamut:
                            lower_in_gamut = False
                        low = value
                    else:
                        # We are still outside the gamut and outside the JND
                        high = value

        color.update(gamutcolor)
