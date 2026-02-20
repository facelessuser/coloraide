"""
Gamut mapping by using ray tracing.

This employs a faster approach than bisecting to reduce chroma.
"""
from __future__ import annotations
import math
from .. import util
from .. import algebra as alg
from . import Fit, clip_channels, coerce_to_rgb
from ..spaces import Prism, Luminant
from ..cat import WHITES
from .tools import adaptive_hue_independent
from ..types import Vector, VectorLike
from typing import Any, TYPE_CHECKING  # noqa: F401

if TYPE_CHECKING:  #pragma: no cover
    from ..color import Color

WHITE = util.xy_to_xyz(WHITES['2deg']['D65'])


def to_rect(coords: Vector, c:int, h: int) -> Vector:
    """Polar to rectangular."""

    coords[c], coords[h] = alg.polar_to_rect(coords[c], coords[h])
    return coords


def to_polar(coords: Vector, c:int, h: int) -> Vector:
    """Rectangular to rectangular."""

    coords[c], coords[h] = alg.rect_to_polar(coords[c], coords[h])
    return coords


def project_onto(a: Vector, b: Vector, o: Vector) -> Vector:
    """
    Using 3 points, create two vectors with a shared origin and project the first vector onto the second.

    - `a`:  point used to define the head of the first vector `OA`.
    - `b`:  point used to define the head of the second vector `OB`.
    - `o`:  the origin/tail point of both vector `OA` and `OB`.
    """

    # Create vector from points
    ox, oy, oz = o
    va1 = a[0] - ox
    va2 = a[1] - oy
    va3 = a[2] - oz
    vb1 = b[0] - ox
    vb2 = b[1] - oy
    vb3 = b[2] - oz

    # Project `vec_oa` onto `vec_ob` and convert back to a point
    n = (va1 * vb1 + va2 * vb2 + va3 * vb3)
    d = (vb1 * vb1 + vb2 * vb2 + vb3 * vb3)

    if d == 0:  # pragma: no cover
        d = alg.EPS
    r = n / d

    # Some spaces may project something that exceeds the range of our target vector.
    if r > 1.0:
        r = 1.0
    elif r < 0.0:  # pragma: no cover
        r = 0.0
    return [vb1 * r + ox, vb2 * r + oy, vb3 * r + oz]


def raytrace_box(
    start: Vector,
    end: Vector,
    bmin: VectorLike = (0.0, 0.0, 0,0),
    bmax: VectorLike = (1.0, 1.0, 1.0)
) -> Vector:
    """
    Return the intersection of an axis aligned box using slab method.

    https://en.wikipedia.org/wiki/Slab_method
    """

    tfar = math.inf
    tnear = -math.inf
    direction = []
    for i in range(3):
        a = start[i]
        b = end[i]
        d = b - a
        direction.append(d)
        bn = bmin[i]
        bx = bmax[i]

        # Non parallel case
        if abs(d) > alg.ATOL:
            inv_d = 1.0 / d
            t1 = (bn - a) * inv_d
            t2 = (bx - a) * inv_d
            tnear = max(min(t1, t2), tnear)
            tfar = min(max(t1, t2), tfar)

        # Parallel case outside
        elif a < bn or a > bx:
            return []

    # No hit
    if tnear > tfar or tfar < 0:
        return []

    # Favor the intersection first in the direction start -> end
    if tnear < 0.0:
        tnear = tfar

    # Point is  close to the surface, so `tnear` could be very large.
    if not math.isfinite(tnear):
        return []

    # Calculate intersection interpolation.
    return [
        start[0] + direction[0] * tnear,
        start[1] + direction[1] * tnear,
        start[2] + direction[2] * tnear
    ]


class RayTrace(Fit):
    """Gamut mapping by using ray tracing."""

    NAME = "raytrace"
    PSPACE = "oklch"

    def fit(
        self,
        color: Color,
        space: str,
        *,
        pspace: str | None = None,
        adaptive: float = 0.0,
        **kwargs: Any
    ) -> None:
        """Scale the color within its gamut but preserve L and h as much as possible."""

        if pspace is None:
            pspace = self.PSPACE
        orig_space = space
        cs = color.CS_MAP[space]

        # Requires an RGB-ish or Prism space, preferably a linear space.
        # Coerce RGB cylinders with no defined RGB space to RGB
        coerced = False
        if not isinstance(cs, Prism) or isinstance(cs, Luminant):
            coerced = True
            cs = coerce_to_rgb(cs)

        # Get the maximum cube size, usually `[1.0, 1.0, 1.0]`
        mx = cs.CHANNELS[0].high

        # If there is a linear version of the RGB space, results will be better if we use that.
        # Recalculate the bounding box relative to the linear version.
        linear = cs.linear()
        if linear and linear in color.CS_MAP:
            subtractive = cs.SUBTRACTIVE
            cs = color.CS_MAP[linear]
            if subtractive != cs.SUBTRACTIVE:
                mx = color.new(space, [cs.CHANNELS[0].low] * 3).convert(linear, in_place=True)[0]
            else:
                mx = color.new(space, [mx] * 3).convert(linear, in_place=True)[0]
            space = linear

        # Get the minimum bounds
        bmax = [mx] * 3
        mn = cs.CHANNELS[0].low
        bmin = [mn] * 3

        orig = color.space()
        mapcolor = color.convert(pspace, norm=False) if orig != pspace else color.clone().normalize(nans=False)
        polar = mapcolor._space.is_polar()
        achroma = mapcolor.clone()

        # Different perceptual spaces may have components in different orders so capture their indexes
        if polar:
            l, c, h = achroma._space.indexes()
            achroma[c] = 0.0
        else:
            l, a, b = achroma._space.indexes()
            achroma[a] = 0.0
            achroma[b] = 0.0

        # If an alpha value is provided for adaptive lightness, calculate a lightness
        # anchor point relative to the hue independent mid point. Scale lightness and
        # chroma by the max lightness to get lightness between 0 and 1.
        if adaptive:
            max_light = color.new('xyz-d65', WHITE).convert(pspace, in_place=True)[l]
            alight = adaptive_hue_independent(
                mapcolor[l] / max_light,
                max(mapcolor[c] if polar else alg.rect_to_polar(mapcolor[a], mapcolor[b])[0], 0) / max_light,
                adaptive
            ) * max_light
            achroma[l] = alight
        else:
            alight = mapcolor[l]

        # Some perceptual spaces, such as CAM16 or HCT, may compensate for adapting
        # luminance which may give an achromatic that is not quite achromatic.
        # Project the lightness point back onto to the gamut's achromatic line.
        anchor = cs.from_base(achroma.convert(space)[:-1]) if coerced else achroma.convert(space)[:-1]
        anchor = project_onto(anchor, bmax, bmin)

        # Return white or black if the achromatic version is not within the RGB cube.
        # HDR colors currently use the RGB maximum lightness. We do not currently
        # clip HDR colors to SDR white, but that could be done if required.
        if anchor == bmax:
            color.update(space, cs.to_base(bmax) if coerced else bmax, mapcolor[-1])
        elif anchor == bmin:
            color.update(space, cs.to_base(bmin) if coerced else bmin, mapcolor[-1])
        else:
            # Ensure we are handling coordinates in the polar space to better retain hue
            if polar:
                start = mapcolor[:-1]
                end = achroma[:-1]
            else:
                start = to_polar(mapcolor[:-1], a, b)
                end = to_polar(achroma[:-1], a, b)
                end[b] = start[b]

            # Offset is required for some perceptual spaces that are sensitive
            # to anchors that get too close to the surface.
            low = mn + 1e-6
            high = mx + 1e-6

            # Use an iterative process of casting rays to find the intersect with the RGB gamut
            # and correcting the intersection onto the LCh chroma reduction path.
            last = mapcolor.convert(space, in_place=True)[:-1]
            if any(mn > x or x > mx for x in last):
                for i in range(4):
                    if i:
                        coords = mapcolor.convert(pspace, in_place=True, norm=False)[:-1]

                        # Project the point onto the desired interpolation path in LCh if applying adaptive luminance
                        if adaptive:
                            if polar:
                                mapcolor[:-1] = project_onto(coords, start, end)
                            else:
                                mapcolor[:-1] = to_rect(project_onto(to_polar(coords, a, b), start, end), a, b)

                        # For constant luminance, just correct lightness and hue in LCh
                        else:
                            coords[l] = start[l]
                            if polar:
                                coords[h] = start[h]
                            else:
                                to_polar(coords, a, b)
                                coords[b] = start[b]
                                to_rect(coords, a, b)
                            mapcolor[:-1] = coords

                        mapcolor.convert(space, in_place=True)

                    # Cast a ray and find the intersection with the gamut surface
                    coords = cs.from_base(mapcolor[:-1]) if coerced else mapcolor[:-1]
                    intersection = raytrace_box(anchor, coords, bmin=bmin, bmax=bmax)

                    # If we cannot find an intersection, reset to last good color and quit
                    if not intersection:
                        mapcolor[:-1] = last
                        break

                    # Adjust anchor point closer to surface to improve results.
                    if i and all(low < x < high for x in coords):
                        anchor = coords

                    # Update color with the intersection point on the RGB surface.
                    last = cs.to_base(intersection) if coerced else intersection
                    mapcolor[:-1] = last
                    continue

            # Remove noise from floating point conversion.
            clip_channels(mapcolor.convert(orig_space, in_place=True))
            color.update(mapcolor)
