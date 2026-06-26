"""
Gamut mapping by using ray tracing.

This employs a faster approach than bisecting to reduce chroma.
"""
from __future__ import annotations
import math
from functools import lru_cache
from .. import util
from .. import algebra as alg
from . import Fit, coerce_to_rgb
from .tools import adaptive_hue_independent
from ..spaces import Space, Prism, Luminant
from ..spaces.oklab import LMS_TO_XYZD65, OKLAB_TO_LMS3, LMS3_TO_OKLAB
from ..cat import WHITES, calc_adaptation_matrices, Bradford, CAT, VonKries
from ..types import Vector, VectorLike, Matrix
from typing import Any, TYPE_CHECKING  # noqa: F401

if TYPE_CHECKING:  #pragma: no cover
    from ..color import Color

WHITE = util.xy_to_xyz(WHITES['2deg']['D65'])
CSS_FAST_PATH = {'oklab', 'oklch'}
TO_RGB = 'TO_RGB'


def to_rect(coords: Vector, c:int, h: int) -> Vector:
    """Polar to rectangular."""

    coords[c], coords[h] = alg.polar_to_rect(coords[c], coords[h])
    return coords


def to_polar(coords: Vector, c:int, h: int) -> Vector:
    """Rectangular to rectangular."""

    coords[c], coords[h] = alg.rect_to_polar(coords[c], coords[h])
    return coords


@lru_cache(maxsize=10)
def get_conversion_matrices(name: str, space: Space, cat: str, adapt: CAT) -> tuple[Matrix, Matrix]:
    """Get and cache conversion matrices to convert from linear RGB to LMS (Oklab variant)."""

    # If we were ever to allow more complicated chromatic adaptation plugins,
    # we may need to default to Bradford as others may not be compatible.
    am = Bradford.MATRIX if not isinstance(adapt, VonKries) else adapt.MATRIX

    d65 = WHITES['2deg']['D65']
    m = space.TO_RGB  # type: ignore[attr-defined]
    if space.WHITE != d65:
        m = alg.matmul_x3(
            m,
            calc_adaptation_matrices(d65, space.WHITE, am),
            dims=alg.D2
        )
    m = alg.matmul_x3(m, LMS_TO_XYZD65, dims=alg.D2)
    return m, alg.inv(m)


def from_oklch(coords: Vector, m: Matrix) -> Vector:
    """Specialized conversion from OkLCh going straight from OkLCh to any linear RGB."""

    return alg.matmul_x3(
        m,
        [c ** 3 for c in alg.matmul_x3(OKLAB_TO_LMS3, to_rect(coords[:], 1, 2), dims=alg.D2_D1)],
        dims=alg.D2_D1
    )


def to_oklch(coords: Vector, m: Matrix) -> Vector:
    """Specialized conversion to OkLCh going straight from any linear RGB to OkLCh."""

    return to_polar(
        alg.matmul_x3(
            LMS3_TO_OKLAB,
            [alg.nth_root(c, 3) for c in alg.matmul_x3(m, coords[:], dims=alg.D2_D1)],
            dims=alg.D2_D1
        ),
        1,
        2
    )


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
        # 64-bit uses a threshold of 1e-12
        # 32-bit should use 1e-6
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


def css_fast_path(
    color: Color,
    cs: Space,
    pspace: str,
    adaptive: float,
    mn: float,
    mx: float,
    **kwargs: Any
) -> None:
    """Path that optimizes conversions for CSS defaults of an Oklab/OkLCh perceptual space and linear RGB target."""

    # RGB linear space
    rspace = cs.NAME

    # Set the minimum bounds
    bmax = [mx] * 3
    bmin = [mn] * 3

    # Ensure we are in the proper perceptual space or normalize values
    orig = color.space()
    mapcolor = color.convert(pspace, norm=False) if orig != pspace else color.clone().normalize(nans=False)
    mapcoords = mapcolor[:-1]

    # Ensure we are working in OkLCh and
    if pspace == 'oklab':
        to_polar(mapcoords, 1, 2)

    # Get Oklab conversion matrices from linear RGB -> Oklab LMS
    adapt = color.CHROMATIC_ADAPTATION
    m, mi = get_conversion_matrices(rspace, cs, adapt, color.CAT_MAP[adapt])

    # Calculate the achromatic version of the color
    achroma = mapcoords[:]
    achroma[1] = 0.0

    # If value is provided for adaptive lightness, calculate a lightness
    # anchor point relative to the hue independent mid point. Scale lightness and
    # chroma by the max lightness to get lightness between 0 and 1.
    if adaptive:
        max_light = color.new('xyz-d65', WHITE).convert(pspace, in_place=True)[0]
        achroma[0] = adaptive_hue_independent(
            mapcoords[0] / max_light,
            max(mapcoords[1], 0) / max_light,
            adaptive
        ) * max_light

    # Calculate achromatic anchor.
    anchor = from_oklch(achroma, m)
    # This allows us to find the maximum lightness for HDR RGB and SDR RGB.
    # Some perceptual spaces do not have a traditional achromatic axis that aligns
    # with the RGB achromatic line, so this would also project and clamp the achromatic
    # value to the RGB achromatic line.
    anchor = project_onto(anchor, bmax, bmin)

    # Return white or black if the achromatic version is not within the RGB cube.
    # HDR colors currently use the RGB maximum lightness. We do not currently
    # clip HDR colors to SDR white, but that could be done if required.
    if anchor == bmax:
        color.update(rspace, bmax, mapcolor[-1])
    elif anchor == bmin:
        color.update(rspace, bmin, mapcolor[-1])
    else:
        # Ensure we are handling coordinates in the polar space to better retain hue
        start = mapcoords[:]
        end = achroma[:]

        # Select an offset from the gamut surface according to unit type (64-bit for Python).
        # 32-bit may require 1e-6
        low = mn + alg.ATOL
        high = mx + alg.ATOL

        # Use an iterative process of casting rays to find the intersect with the RGB gamut
        # and correcting the intersection onto the LCh chroma reduction path.
        mapcoords[:] = from_oklch(mapcoords, m)
        last = mapcoords[:]
        if any(mn > x or x > mx for x in last):
            for i in range(4):
                if i:
                    coords = to_oklch(mapcoords, mi)

                    # Project the point onto the desired interpolation path in LCh if applying adaptive luminance
                    if adaptive:
                        coords = project_onto(coords, start, end)

                    # For constant luminance, just correct lightness and hue in LCh
                    else:
                        coords[0] = start[0]
                        coords[2] = start[2]
                    mapcoords[:] = from_oklch(coords, m)

                # Cast a ray and find the intersection with the gamut surface
                coords = mapcoords[:]
                intersection = raytrace_box(anchor, coords, bmin=bmin, bmax=bmax)

                # If we cannot find an intersection, reset to last good color and quit
                if not intersection:
                    mapcoords[:] = last
                    break

                # Adjust anchor point closer to surface to improve results.
                if i and all(low < x < high for x in coords):
                    anchor = coords

                # Update color with the intersection point on the RGB surface.
                last = intersection
                mapcoords[:] = last
                continue

        # Remove noise from floating point conversion.
        color.update(rspace, [max(mn, min(mx, x)) for x in mapcoords], mapcolor[-1])


def generic_path(
    color: Color,
    rspace: str,
    cs: Space,
    pspace: str,
    adaptive: float,
    mn: float,
    mx: float,
    coerced: bool,
    **kwargs: Any
) -> None:
    """
    Generic path for any perceptual space and coerced RGB handling that can be slower due to generalized logic.

    Any perceptual space (Lab/LCh) can be used as the working space. In addition, RGB spaces do not have to be linear,
    even though they are preferred. Lastly, cylindrical spaces with no associated RGB gamut can be coerced into a
    geometric cube to allow for an increased chance of successful gamut mapping.
    """

    # Set the minimum bounds
    bmax = [mx] * 3
    bmin = [mn] * 3

    # Ensure we are in the proper perceptual space or normalize values
    orig = color.space()
    mapcolor = color.convert(pspace, norm=False) if orig != pspace else color.clone().normalize(nans=False)

    # Different perceptual spaces may have components in different orders so capture their indexes
    # Calculate the achromatic version of the color
    polar = mapcolor._space.is_polar()
    achroma = mapcolor.clone()
    if polar:
        l, c, h = achroma._space.indexes()
        achroma[c] = 0.0
    else:
        l, a, b = achroma._space.indexes()
        achroma[a] = 0.0
        achroma[b] = 0.0

    # If value is provided for adaptive lightness, calculate a lightness
    # anchor point relative to the hue independent mid point. Scale lightness and
    # chroma by the max lightness to get lightness between 0 and 1.
    if adaptive:
        max_light = color.new('xyz-d65', WHITE).convert(pspace, in_place=True)[l]
        achroma[l] = adaptive_hue_independent(
            mapcolor[l] / max_light,
            max(mapcolor[c] if polar else alg.rect_to_polar(mapcolor[a], mapcolor[b])[0], 0) / max_light,
            adaptive
        ) * max_light

    # Calculate achromatic anchor.
    anchor = cs.from_base(achroma.convert(rspace)[:-1]) if coerced else achroma.convert(rspace)[:-1]
    # This allows us to find the maximum lightness for HDR RGB and SDR RGB.
    # Some perceptual spaces do not have a traditional achromatic axis that aligns
    # with the RGB achromatic line, so this would also project and clamp the achromatic
    # value to the RGB achromatic line.
    anchor = project_onto(anchor, bmax, bmin)

    # Return white or black if the achromatic version is not within the RGB cube.
    # HDR colors currently use the RGB maximum lightness. We do not currently
    # clip HDR colors to SDR white, but that could be done if required.
    if anchor == bmax:
        color.update(rspace, cs.to_base(bmax) if coerced else bmax, mapcolor[-1])
    elif anchor == bmin:
        color.update(rspace, cs.to_base(bmin) if coerced else bmin, mapcolor[-1])
    else:
        # Ensure we are handling coordinates in the polar space to better retain hue
        if polar:
            start = mapcolor[:-1]
            end = achroma[:-1]
        else:
            start = to_polar(mapcolor[:-1], a, b)
            end = to_polar(achroma[:-1], a, b)
            end[b] = start[b]

        # Select an offset from the gamut surface according to unit type (64-bit for Python).
        # 32-bit may require 1e-6
        low = mn + alg.ATOL
        high = mx + alg.ATOL

        # Use an iterative process of casting rays to find the intersect with the RGB gamut
        # and correcting the intersection onto the LCh chroma reduction path.
        last = mapcolor.convert(rspace, in_place=True)[:-1]
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

                    mapcolor.convert(rspace, in_place=True)

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
        if coerced:
            mapcolor[:-1] = cs.to_base([max(mn, min(mx, x)) for x in cs.from_base(mapcolor[:-1])])
        else:
            mapcolor[:-1] = [max(mn, min(mx, x)) for x in mapcolor[:-1]]
        color.update(mapcolor)


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
        """Use ray tracing with a linear RGB space for a geometric approach to reducing chroma."""

        if pspace is None:
            pspace = self.PSPACE
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

        # Get minimum
        mn = cs.CHANNELS[0].low

        # If we are gamut mapping using Oklab/OkLCh, per the CSS spec, and we are
        # gamut mapping within an linear RGB gamut, use the CSS fast path that
        # reduces overhead and is optimized for OkLCh and linear RGB.
        if pspace in CSS_FAST_PATH and not coerced and hasattr(cs, TO_RGB):
            css_fast_path(color, cs, pspace, adaptive, mn, mx)
        else:
            generic_path(color, space, cs, pspace, adaptive, mn, mx, coerced)
