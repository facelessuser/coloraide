"""
Gamut mapping by using ray tracing.

This employs a faster approach than bisecting to reduce chroma.
"""
from __future__ import annotations
from ..gamut import Fit
from ..spaces import RGBish
from .. import algebra as alg
from .. import util
from ..cat import WHITES
import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

WHITE = util.xy_to_xyz(WHITES['2deg']['D65'])
BLACK = [0, 0, 0]


class OkLChRayTrace(Fit):
    """Gamut mapping by using ray tracing."""

    NAME = "oklch-raytrace"
    SPACE = "oklch"
    MAX_LIGHTNESS = 1
    MIN_LIGHTNESS = 0
    TRACES = 3
    BACKOFF_MAP = {
        1: [0.98],
        2: [0.88, 0.98],
        3: [0.9, 0.95, 0.98]
    }

    def fit(self, color: Color, space: str, *, traces: int = 0, **kwargs: Any) -> None:
        """Scale the color within its gamut but preserve L and h as much as possible."""

        # Requires an RGB-ish space, preferably a linear space.
        cs = color.CS_MAP[space]
        if not isinstance(cs, RGBish):
            raise ValueError("Scaling only works in an RGBish color space, not {}".format(type(color.CS_MAP[space])))

        # For now, if a non-linear CSS variant is specified, just use the linear form.
        linear = cs.linear()
        if linear and linear in color.CS_MAP:
            space = linear

        orig = color.space()
        mapcolor = color.convert(self.SPACE, norm=False) if orig != self.SPACE else color.clone().normalize(nans=False)
        l, c, h = mapcolor._space.indexes()  # type: ignore[attr-defined]

        # Return white for white or black.
        lightness = mapcolor[l]
        if lightness >= self.MAX_LIGHTNESS or math.isclose(lightness, self.MAX_LIGHTNESS, abs_tol=1e-6):
            color.update('xyz-d65', WHITE, mapcolor[-1])
            return
        elif lightness <= self.MIN_LIGHTNESS:
            color.update('xyz-d65', BLACK, mapcolor[-1])
            return

        # Perform the iteration(s) scaling within the RGB space but afterwards preserving all but chroma
        gamutcolor = color.convert(space, norm=False) if orig != space else color.clone().normalize(nans=False)
        achroma = mapcolor.clone().set('c', 0).convert(space)

        L = self.SPACE + '.' + str(l)
        C = self.SPACE + '.' + str(c)
        H = self.SPACE + '.' + str(h)

        # Create a line from our color to color with zero lightness.
        # Trace the line to the RGB cube finding the face and the point where it intersects.
        # Back off chroma on each iteration, less as we get closer.
        size = [1.0, 1.0, 1.0]
        backoff = self.BACKOFF_MAP[traces if traces else self.TRACES]
        for i in range(len(backoff)):
            face, result = alg.raytrace_cube(size, gamutcolor.coords(), achroma.coords())
            if face:
                gamutcolor[:-1] = result
                # Back off chroma and try with a closer point
                gamutcolor.set(
                    {
                        L: mapcolor[l],
                        C: lambda x, i=i: self.backoff(x, mapcolor[c], backoff[i]),
                        H: mapcolor[h]
                    }
                )
            else:
                # We were already within the cube
                break

        # Finally, clip the color just in case
        gamutcolor[:-1] = [alg.clamp(x, 0, 1) for x in gamutcolor[:-1]]
        color.update(gamutcolor)

    def backoff(self, c: float, original: float = 0.0, backoff: float = 0.0) -> float:
        """Back off chroma."""

        d = original - c
        b = d * backoff
        if d > 0.05:
            return original - b
        return c
