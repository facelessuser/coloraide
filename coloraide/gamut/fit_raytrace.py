"""
Gamut mapping by using ray tracing.

This employs a faster approach than bisecting to reduce chroma.
"""
from __future__ import annotations
from .. import algebra as alg
from ..gamut import Fit
from ..spaces import Space, RGBish, HSLish, HSVish, HWBish
from ..spaces.hsl import hsl_to_srgb, srgb_to_hsl
from ..spaces.hsv import hsv_to_srgb, srgb_to_hsv
from ..spaces.hwb import hwb_to_srgb, srgb_to_hwb
from ..spaces.srgb_linear import sRGBLinear
from ..types import Vector
from typing import TYPE_CHECKING, Callable, Any  # noqa: F401

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


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
        raise ValueError('Cannot coerce {} to an RGB space.'.format(cs.NAME))

    class RGB(sRGBLinear):
        """Custom RGB class."""

        NAME = '-rgb-{}'.format(cs.NAME)
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


def raytrace_box(size: Vector, start: Vector, end: Vector) -> tuple[int, Vector]:
    """
    Returns the face and the intersection tuple of an array from start to end of a cube of size [x, y, z].

    - 0: None, (point is None)
    - 1: intersection with x==0 face,
    - 2: intersection with x==size[0] face,
    - 3: intersection with y==0 face,
    - 4: intersection with y==size[1] face,
    - 5: intersection with z==0 face,
    - 6: intersection with z==size[2] face,

    The cube is an axis-aligned cube: (0,0,0)-(size[0],size[1],size[2]).

    ```
    mwt (https://math.stackexchange.com/users/591865/mwt),
    Finding the side of a cube intersecting a line using the shortest computation,
    URL (version: 2020-08-01): https://math.stackexchange.com/q/3776157
    ```
    """

    # Negated deltas
    ndx = start[0] - end[0]
    ndy = start[1] - end[1]
    ndz = start[2] - end[2]

    # Sizes scaled by the negated deltas
    sxy = ndx * size[1]
    sxz = ndx * size[2]
    syx = ndy * size[0]
    syz = ndy * size[2]
    szx = ndz * size[0]
    szy = ndz * size[1]

    # Cross terms
    cxy = end[0] * start[1] - end[1] * start[0]
    cxz = end[0] * start[2] - end[2] * start[0]
    cyz = end[1] * start[2] - end[2] * start[1]

    # Absolute delta products
    axy = abs(ndx * ndy)
    axz = abs(ndx * ndz)
    ayz = abs(ndy * ndz)
    axyz = abs(ndz * axy)

    # Default to "no intersection"
    face_num = 0
    face_tau = abs(ndz * axy)

    # These variables are no longer used:
    del ndx, ndy, ndz

    if start[0] < 0 and 0 < end[0]:
        # Face 1: x == 0
        tau = -start[0] * ayz
        if tau <= face_tau and cxy >= 0 and cxz >= 0 and cxy <= -sxy and cxz <= -sxz:
            face_tau = tau
            face_num = 1

    elif end[0] < size[0] and size[0] < start[0]:
        # Face 2: x == size[0]
        tau = (start[0] - size[0]) * ayz
        if tau <= face_tau and cxy <= syx and cxz <= szx and cxy >= syx - sxy and cxz >= szx - sxz:
            face_tau = tau
            face_num = 2

    if start[1] < 0 and end[1] > 0:
        # Face 3: y == 0
        tau = -start[1] * axz
        if tau <= face_tau and cxy <= 0 and cyz >= 0 and cxy >= syx and cyz <= -syz:
            face_tau = tau
            face_num = 3

    elif start[1] > size[1] and end[1] < size[1]:
        # Face 4: y == size[1]
        tau = (start[1] - size[1]) * axz
        if tau <= face_tau and cxy >= -sxy and cyz <= szy and cxy <= syx - sxy and cyz >= szy - syz:
            face_tau = tau
            face_num = 4

    if start[2] < 0 and end[2] > 0:
        # Face 5: z == 0
        tau = -start[2] * axy
        if tau <= face_tau and cxz <= 0 and cyz <= 0 and cxz >= szx and cyz >= szy:
            face_tau = tau
            face_num = 5

    elif start[2] > size[2] and end[2] < size[2]:
        # Face 6: z == size[2]
        tau = (start[2] - size[2]) * axy
        if tau <= face_tau and cxz >= -sxz and cyz >= -syz and cxz <= szx - sxz and cyz <= szy - syz:
            face_tau = tau
            face_num = 6

    if face_num > 0:
        # Handle a cases where the ray is perpendicular (and other similar cases).
        # Use the face to identify the boundary limit and calculate intersection via interpolation.
        if axyz == 0:
            idx = (face_num - 1) // 2
            boundary = ((face_num - 1) % 2) * size[idx]
            factor = alg.ilerp(start[idx], end[idx], boundary)
            return (
                face_num,
                [
                    alg.lerp(start[0], end[0], factor),
                    alg.lerp(start[1], end[1], factor),
                    alg.lerp(start[2], end[2], factor),
                ]
            )

        tend = face_tau / axyz
        tstart = 1.0 - tend
        return (
            face_num,
            [
                tstart * start[0] + tend * end[0],
                tstart * start[1] + tend * end[1],
                tstart * start[2] + tend * end[2]
            ]
        )

    return face_num, []  # pragma: no cover


class RayTrace(Fit):
    """Gamut mapping by using ray tracing."""

    NAME = "raytrace"
    SPACE = "lch-d65"

    def fit(self, color: Color, space: str, *, lch: str | None = None, **kwargs: Any) -> None:
        """Scale the color within its gamut but preserve L and h as much as possible."""

        if lch is None:
            lch = self.SPACE

        # Requires an RGB-ish space, preferably a linear space.
        coerced = None
        cs = color.CS_MAP[space]

        # Coerce RGB cylinders with no defined RGB space to RGB
        if not isinstance(cs, RGBish):
            coerced = color
            Color_, space = coerce_to_rgb(type(color), cs)
            cs = Color_.CS_MAP[space]
            color = Color_(color)

        # For now, if a non-linear CSS variant is specified, just use the linear form.
        linear = cs.linear()  # type: ignore[attr-defined]
        if linear and linear in color.CS_MAP:
            space = linear

        orig = color.space()
        mapcolor = color.convert(lch, norm=False) if orig != lch else color.clone().normalize(nans=False)
        l, c, h = mapcolor._space.indexes()  # type: ignore[attr-defined]
        achroma = mapcolor.clone().set(str(c), 0).convert(space)[:-1]

        # Return white or black if the achromatic version is not within the RGB cube.
        mn, mx = alg.minmax(achroma)
        if mx >= 1:
            color.update(space, [1.0, 1.0, 1.0], mapcolor[-1])
        elif mn <= 0:
            color.update(space, [0.0, 0.0, 0.0], mapcolor[-1])
        else:
            gamutcolor = color.convert(space, norm=False) if orig != space else color.clone().normalize(nans=False)

            L = lch + '.' + str(l)
            H = lch + '.' + str(h)

            # Create a line from our color to color with zero lightness.
            # Trace the line to the RGB cube finding the face and the point
            # where it intersects. Correct L and H, which will likely shift the point.
            # Take two rounds to get us as close as we can get.
            size = [1.0, 1.0, 1.0]
            xa, ya, za = achroma
            for i in range(3):
                # On subsequent runs correct L and H and
                # extend the vector in case we are now under saturated
                if i:
                    gamutcolor.set({L: mapcolor[l], H: mapcolor[h]})
                    x, y, z = gamutcolor[:-1]
                    coords = [alg.lerp(xa, x, 100), alg.lerp(ya, y, 100), alg.lerp(za, z, 100)]
                else:
                    coords = gamutcolor[:-1]
                face, intersection = raytrace_box(size, coords, achroma)
                if face:
                    gamutcolor[:-1] = intersection
                    continue
                break  # pragma: no cover

            gamutcolor[:-1] = [alg.clamp(x, 0.0, 1.0) for x in gamutcolor[:-1]]
            color.update(gamutcolor)

        # If we have coerced a space to RGB, update the original
        if coerced:
            coerced.update(color)
