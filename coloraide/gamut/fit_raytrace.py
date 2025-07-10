"""
Gamut mapping by using ray tracing.

This employs a faster approach than bisecting to reduce chroma.
"""
from __future__ import annotations
import math
from functools import lru_cache
from .. import util
from .. import algebra as alg
from ..gamut import Fit
from ..cat import WHITES
from ..spaces import RGBish, Prism, Space, HSLish, HSVish, HWBish
from ..spaces.hsl import hsl_to_srgb, srgb_to_hsl
from ..spaces.hsv import hsv_to_srgb, srgb_to_hsv
from ..spaces.hwb import hwb_to_hsv, hsv_to_hwb
from ..spaces.srgb_linear import sRGBLinear
from .tools import adaptive_hue_independent
from ..types import Vector, VectorLike
from typing import Callable, Any, TYPE_CHECKING  # noqa: F401

if TYPE_CHECKING:  #pragma: no cover
    from ..color import Color

WHITE = util.xy_to_xyz(WHITES['2deg']['D65'])


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
    r = (va1 * vb1 + va2 * vb2 + va3 * vb3) / (vb1 * vb1 + vb2 * vb2 + vb3 * vb3)
    # Some spaces may project something that exceeds the range of our target vector.
    if r > 1.0:
        r = 1.0
    elif r < 0.0:  # pragma: no cover
        r = 0.0
    return [vb1 * r + ox, vb2 * r + oy, vb3 * r + oz]


def hwb_to_srgb(coords: Vector) -> Vector:  # pragma: no cover
    """Convert HWB to sRGB."""

    return hsv_to_srgb(hwb_to_hsv(coords))


def srgb_to_hwb(coords: Vector) -> Vector:  # pragma: no cover
    """Convert sRGB to HWB."""

    return hsv_to_hwb(srgb_to_hsv(coords))


def to_rect(coords: Vector, c:int, h: int) -> Vector:
    """Polar to rectangular."""

    coords[c], coords[h] = alg.polar_to_rect(coords[c], coords[h])
    return coords


def to_polar(coords: Vector, c:int, h: int) -> Vector:
    """Rectangular to rectangular."""

    coords[c], coords[h] = alg.rect_to_polar(coords[c], coords[h])
    return coords


@lru_cache(maxsize=20, typed=True)
def coerce_to_rgb(cs: Space) -> Space:
    """
    Coerce an HSL, HSV, or HWB color space to RGB to allow us to ray trace the gamut.

    It is rare to have a color space that is bound to an RGB gamut that does not exist as an RGB
    defined RGB space. HPLuv is one that is defined only as a cylindrical, HSL-like space. Okhsl
    and Okhsv are another whose gamut is meant to target sRGB, but it is very fuzzy and has sRGB
    colors not quite in gamut, and others that exceed the sRGB gamut.

    For gamut mapping, RGB cylindrical spaces can be coerced into an RGB form using traditional
    HSL, HSV, or HWB approaches which is good enough.
    """

    if isinstance(cs, HSLish):
        to_ = hsl_to_srgb  # type: Callable[[Vector], Vector]
        from_ = srgb_to_hsl  # type: Callable[[Vector], Vector]
    elif isinstance(cs, HSVish):
        to_ = hsv_to_srgb
        from_ = srgb_to_hsv
    elif isinstance(cs, HWBish):  # pragma: no cover
        to_ = hwb_to_srgb
        from_ = srgb_to_hwb
    else:  # pragma: no cover
        raise ValueError(f'Cannot coerce {cs.NAME} to an RGB space.')

    class RGB(sRGBLinear):
        """Custom RGB class."""

        NAME = f'-rgb-{cs.NAME}'
        BASE = cs.NAME
        GAMUT_CHECK = None
        CLIP_SPACE = None
        WHITE = cs.WHITE
        DYAMIC_RANGE = cs.DYNAMIC_RANGE
        INDEXES = cs.indexes()
        # Scale saturation and lightness (or HWB whiteness and blackness)
        SCALE_SAT = cs.CHANNELS[INDEXES[1]].high
        SCALE_LIGHT = cs.CHANNELS[INDEXES[1]].high

        def to_base(self, coords: Vector) -> Vector:
            """Convert from RGB to HSL."""

            coords = from_(coords)
            if self.SCALE_SAT != 1:
                coords[1] *= self.SCALE_SAT
            if self.SCALE_LIGHT != 1:
                coords[2] *= self.SCALE_LIGHT
            ordered = [0.0, 0.0, 0.0]
            for e, c in enumerate(coords):
                ordered[self.INDEXES[e]] = c
            return ordered

        def from_base(self, coords: Vector) -> Vector:
            """Convert from HSL to RGB."""

            coords = [coords[i] for i in self.INDEXES]
            if self.SCALE_SAT != 1:
                coords[1] /= self.SCALE_SAT
            if self.SCALE_LIGHT != 1:
                coords[2] /= self.SCALE_LIGHT
            coords = to_(coords)
            return coords

    return RGB()


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
        if d:
            inv_d = 1 / d
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
    if tnear < 0:
        tnear = tfar

    # An infinitesimally small point was used, not a ray.
    # The origin is the intersection. Our use case will
    # discard such scenarios, but others may wish to set
    # intersection to origin.
    if math.isinf(tnear):
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
    PSPACE = "oklab"

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
        cs = color.CS_MAP[space]

        # Requires an RGB-ish or Prism space, preferably a linear space.
        # Coerce RGB cylinders with no defined RGB space to RGB
        coerced = False
        if not isinstance(cs, (Prism, RGBish)):
            coerced = True
            cs = coerce_to_rgb(cs)

        # Get the maximum cube size, usually `[1.0, 1.0, 1.0]`
        bmax = [chan.high for chan in cs.CHANNELS]

        # If there is a linear version of the RGB space, results will be better if we use that.
        # Recalculate the bounding box relative to the linear version.
        linear = cs.linear()
        if linear and linear in color.CS_MAP:
            bmax = color.new(space, bmax).convert(linear, in_place=True)[:-1]
            space = linear

        orig = color.space()
        mapcolor = color.convert(pspace, norm=False) if orig != pspace else color.clone().normalize(nans=False)
        polar = mapcolor._space.is_polar()
        achroma = mapcolor.clone()

        # Different perceptual spaces may have components in different orders so capture their indexes
        if polar:
            l, c, h = achroma._space.indexes()
            achroma[c] = 0
        else:
            l, a, b = mapcolor._space.indexes()
            achroma[a] = 0
            achroma[b] = 0

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
        # luminance which may give an achromatic that is not quite achromatic,
        # causing a more sizeable delta between the max and min value in the
        # achromatic RGB color. To compensate for such deviations, take the
        # average value of the RGB components and use that as the achromatic point.
        anchor = achroma.convert(space)[:-1]
        anchor = [sum(cs.from_base(anchor) if coerced else anchor) / 3] * 3

        # Return white or black if the achromatic version is not within the RGB cube.
        # HDR colors currently use the RGB maximum lightness. We do not currently
        # clip HDR colors to SDR white, but that could be done if required.
        bmx = bmax[0]
        point = anchor[0]
        if point >= bmx:
            color.update(space, cs.to_base(bmax) if coerced else bmax, mapcolor[-1])
        elif point <= 0:
            bmin = [0.0, 0.0, 0.0]
            color.update(space, cs.to_base(bmin) if coerced else bmin, mapcolor[-1])
        else:
            # Create a ray from our current color to the anchor.
            # Trace the line to the RGB cube finding the intersection.
            # In between iterations, correct the L and H and then cast a ray
            # to the new corrected color finding the intersection again.
            if polar:
                start = to_rect(mapcolor[:-1], c, h)
                end = to_rect(achroma[:-1], c, h)
            else:
                start = mapcolor[:-1]
                end = achroma[:-1]

            mapcolor.convert(space, in_place=True)

            # Threshold for anchor adjustment
            low = 1e-6
            high = bmx - low

            for i in range(4):
                if i:
                    # Project the point onto the desired interpolation path
                    coords = mapcolor.convert(pspace, in_place=True, norm=False)[:-1]
                    if polar:
                        mapcolor[:-1] = to_polar(project_onto(to_rect(coords, c, h), start, end), c, h)
                    else:
                        mapcolor[:-1] = project_onto(coords, start, end)
                    mapcolor.convert(space, in_place=True)

                coords = cs.from_base(mapcolor[:-1]) if coerced else mapcolor[:-1]
                intersection = raytrace_box(anchor, coords, bmax=bmax)

                # Adjust anchor point closer to surface to improve results for some spaces.
                # Don't move point too close to the surface to avoid corner cases with some spaces.
                if i and all(low < x < high for x in coords):
                    anchor = coords

                # Update color with the intersection point on the RGB surface.
                if intersection:
                    mapcolor[:-1] = cs.to_base(intersection) if coerced else intersection
                    continue
                break  # pragma: no cover

            # Remove noise from floating point conversion.
            if coerced:
                color.update(
                    space,
                    cs.to_base([alg.clamp(x, 0.0, bmx) for x in cs.from_base(mapcolor[:-1])]),
                    mapcolor[-1]
                )
            else:
                color.update(space, [alg.clamp(x, 0.0, bmx) for x in mapcolor[:-1]], mapcolor[-1])
