"""
Gamut mapping by using ray tracing.

This employs a faster approach than bisecting to reduce chroma.
"""
from __future__ import annotations
import math
from .. import algebra as alg
from ..gamut import Fit
from ..spaces import Space, RGBish, HSLish, HSVish, HWBish
from ..spaces.hsl import hsl_to_srgb, srgb_to_hsl
from ..spaces.hsv import hsv_to_srgb, srgb_to_hsv
from ..spaces.hwb import hwb_to_hsv, hsv_to_hwb
from ..spaces.srgb_linear import sRGBLinear
from .tools import adaptive_hue_independent
from ..types import Vector, VectorLike
from typing import TYPE_CHECKING, Callable, Any  # noqa: F401

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def project_onto(a: Vector, b: Vector, o: Vector) -> Vector:
    """
    Using 3 points, create two vectors with a shared origin and project the first vector onto the second.

    - `a`:  point used to define the head of the first vector `OA`.
    - `b`:  point used to define the head of the second vector `OB`.
    - `o`:  the origin/tail point of both vector `OA` and `OB`.
    """

    # Create vector from points
    ox, oy, oz = o
    vec_oa = [a[0] - ox, a[1] - oy, a[2] - oz]
    vec_ob = [b[0] - ox, b[1] - oy, b[2] - oz]
    # Project `vec_oa` onto `vec_ob` and convert back to a point
    r = alg.matmul_x3(vec_oa, vec_ob, dims=alg.D1) / alg.matmul_x3(vec_ob, vec_ob, dims=alg.D1)
    # Some spaces may project something that exceeds the range of our target vector.
    if r > 1.0:
        r = 1.0
    elif r < 0.0:  # pragma: no cover
        r = 0.0
    return [vec_ob[0] * r + ox, vec_ob[1] * r + oy, vec_ob[2] * r + oz]


def hwb_to_srgb(coords: Vector) -> Vector:  # pragma: no cover
    """Convert HWB to sRGB."""

    return hsv_to_srgb(hwb_to_hsv(coords))


def srgb_to_hwb(coords: Vector) -> Vector:  # pragma: no cover
    """Convert sRGB to HWB."""

    return hsv_to_hwb(srgb_to_hsv(coords))


def coerce_to_rgb(OrigColor: type[Color], cs: Space) -> tuple[type[Color], str]:
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
        INDEXES = cs.indexes()  # type: ignore[attr-defined]
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

    class ColorRGB(OrigColor):  # type: ignore[valid-type, misc]
        """Custom color."""

    ColorRGB.register(RGB())

    return ColorRGB, RGB.NAME


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
        polar = color.CS_MAP[pspace].is_polar()

        cs = color.CS_MAP[space]
        bmax = [1.0, 1.0, 1.0]

        # Requires an RGB-ish space, preferably a linear space.
        # Coerce RGB cylinders with no defined RGB space to RGB
        coerced = None
        if not isinstance(cs, RGBish):
            coerced = color
            Color_, space = coerce_to_rgb(type(color), cs)
            cs = Color_.CS_MAP[space]
            color = Color_(color)

        # If there is a linear version of the RGB space, results will be
        # better if we use that. If the target RGB space is HDR, we need to
        # calculate the bounding box size based on the HDR limit in the linear space.
        sdr = cs.DYNAMIC_RANGE != 'hdr'
        linear = cs.linear()  # type: ignore[attr-defined]
        if linear and linear in color.CS_MAP:
            if not sdr:
                bmax = color.new(space, [chan.high for chan in cs.CHANNELS]).convert(linear)[:-1]
            space = linear

        orig = color.space()
        mapcolor = color.convert(pspace, norm=False) if orig != pspace else color.clone().normalize(nans=False)
        achroma = mapcolor.clone()

        # Different perceptual spaces may have components in different orders, account for this
        if polar:
            l, c, h = achroma._space.indexes()  # type: ignore[attr-defined]
            light = mapcolor[l]
            chroma = mapcolor[c]
            hue = mapcolor[h]
            ab = alg.polar_to_rect(chroma, hue)
            achroma[c] = 0
        else:
            l, a, b = mapcolor._space.indexes()  # type: ignore[attr-defined]
            light = mapcolor[l]
            ab = (mapcolor[a], mapcolor[b])
            chroma, hue = alg.rect_to_polar(*ab)
            achroma[a] = 0
            achroma[b] = 0

        # If an alpha value is provided for adaptive lightness, calculate a lightness
        # anchor point relative to the hue independent mid point. Scale lightness and
        # chroma by the max lightness to get lightness between 0 and 1.
        if adaptive:
            max_light = color.new(space, [1.0, 1.0, 1.0]).convert(pspace)[l]
            alight = adaptive_hue_independent(light / max_light, max(chroma, 0) / max_light, adaptive) * max_light
            achroma[l] = alight
        else:
            alight = light

        # Some perceptual spaces, such as CAM16 or HCT, may compensate for adapting
        # luminance which may give an achromatic that is not quite achromatic,
        # causing a more sizeable delta between the max and min value in the
        # achromatic RGB color. To compensate for such deviations, take the
        # average value of the RGB components and use that as the achromatic point.
        anchor = [sum(achroma.convert(space)[:-1]) / 3] * 3

        # Return white or black if the achromatic version is not within the RGB cube.
        # HDR colors currently use the RGB maximum lightness. We do not currently
        # clip HDR colors to SDR white, but that could be done if required.
        bmx = bmax[0]
        point = anchor[0]
        if point >= bmx:
            color.update(space, bmax, mapcolor[-1])
        elif point <= 0:
            color.update(space, [0.0, 0.0, 0.0], mapcolor[-1])
        else:
            # Create a ray from our current color to the color with zero chroma.
            # Trace the line to the RGB cube finding the intersection.
            # In between iterations, correct the L and H and then cast a ray
            # to the new corrected color finding the intersection again.
            mapcolor.convert(space, in_place=True)

            if adaptive:
                # Interpolation path
                start = [light, *ab]
                end = [alight, 0.0, 0.0]

            # Threshold for anchor adjustment
            low = 1e-6
            high = bmx - low

            for i in range(4):
                if i:
                    mapcolor.convert(pspace, in_place=True, norm=False)

                    # Correct the point onto the desired interpolation path
                    if adaptive:
                        if polar:
                            mapcolor[l], a_, b_ = project_onto(
                                [mapcolor[l], *alg.polar_to_rect(mapcolor[c], mapcolor[h])],
                                start,
                                end
                            )
                            mapcolor[c], mapcolor[h] = alg.rect_to_polar(a_,b_)
                        else:
                            mapcolor[l], mapcolor[a], mapcolor[b] = project_onto(
                                [mapcolor[l], mapcolor[a], mapcolor[b]],
                                start,
                                end
                            )

                    # Simple correction for constant lightness
                    else:
                        mapcolor[l] = alight
                        if polar:
                            mapcolor[h] = hue
                        else:
                            mapcolor[a], mapcolor[b] = alg.polar_to_rect(
                                alg.rect_to_polar(mapcolor[a], mapcolor[b])[0],
                                hue
                            )

                    mapcolor.convert(space, in_place=True)

                coords = mapcolor[:-1]
                intersection = raytrace_box(anchor, coords, bmax=bmax)

                # Adjust anchor point closer to surface to improve results for some spaces.
                # Don't move point too close to the surface to avoid corner cases with some spaces.
                if i and all(low < x < high for x in coords):
                    anchor = coords

                # Update color with the intersection point on the RGB surface.
                if intersection:
                    mapcolor[:-1] = intersection
                    continue
                break  # pragma: no cover

            # Remove noise from floating point conversion.
            color.update(space, [alg.clamp(x, 0.0, bmx) for x in mapcolor[:-1]], mapcolor[-1])

        # If we have coerced a space to RGB, update the original
        if coerced:
            coerced.update(color)
