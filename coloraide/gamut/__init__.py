"""Gamut handling."""
from __future__ import annotations
import math
from abc import ABCMeta, abstractmethod
from functools import lru_cache
from . import pointer
from . import visible_spectrum
from .. import util
from .. import algebra as alg
from ..channels import FLG_ANGLE
from ..types import Plugin, Vector, VectorLike
from ..spaces import Prism, Luminant, Space, HSLish, HSVish, HWBish
from ..spaces.hsl import hsl_to_srgb, srgb_to_hsl
from ..spaces.hsv import hsv_to_srgb, srgb_to_hsv
from ..spaces.hwb import hwb_to_hsv, hsv_to_hwb
from ..spaces.srgb_linear import sRGBLinear
from typing import Any, TYPE_CHECKING, Callable  # noqa: F401

if TYPE_CHECKING:  #pragma: no cover
    from ..color import Color

__all__ = ('clip_channels', 'verify', 'Fit', 'pointer', 'visible_spectrum', 'scale_rgb', 'coerce_to_rgb')

SPECIAL_GAMUTS = {
    'pointer-gamut': {
        'check': pointer.in_pointer_gamut,
        'fit': pointer.fit_pointer_gamut
    },
    'macadam-limits': {
        'check': visible_spectrum.in_macadam_limits,
        'fit': visible_spectrum.fit_macadam_limits
    }
}   # type: dict[str, dict[str, Callable[..., Any]]]


def hwb_to_srgb(coords: Vector) -> Vector:  # pragma: no cover
    """Convert HWB to sRGB."""

    return hsv_to_srgb(hwb_to_hsv(coords))


def srgb_to_hwb(coords: Vector) -> Vector:  # pragma: no cover
    """Convert sRGB to HWB."""

    return hsv_to_hwb(srgb_to_hsv(coords))


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
        SCALE_SAT = cs.channels[INDEXES[1]].high
        SCALE_LIGHT = cs.channels[INDEXES[2]].high

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


def adjust_luminance(color: Color, Y: float, white: VectorLike) -> None:
    """Adjust luminance of a color."""

    with color.within('xyz-d65') as c:
        c.convert('xyz-d65', in_place=True)
        d65 = c._space.WHITE
        adapt = d65 != white
        xyz = c.chromatic_adaptation(d65, white, c[:-1]) if adapt else c[:-1]
        if xyz[1] > Y:
            xyz = util.xy_to_xyz(util.xyz_to_xyY(xyz, white)[:-1], Y)
            c[:-1] = c.chromatic_adaptation(white, d65, xyz) if adapt else xyz


def scale_rgb(
    color: Color,
    *,
    scale_space: str,
    clip_negative: bool = False,
    max_saturation: bool = False
) -> None:
    """Apply color scaling."""

    cs = color.CS_MAP[scale_space]
    orig_space = scale_space

    # Requires an RGB-ish or Prism space, preferably a linear space.
    # Coerce RGB cylinders with no defined RGB space to RGB
    coerced = False
    if not isinstance(cs, Prism) or isinstance(cs, Luminant):
        coerced = True
        cs = coerce_to_rgb(cs)

    # If there is a linear version of the RGB space, results will be better if we use that.
    maximum = cs.channels[0].high
    linear = cs.linear()
    if linear and linear in color.CS_MAP:
        subtractive = cs.SUBTRACTIVE
        cs = color.CS_MAP[linear]
        if subtractive != cs.SUBTRACTIVE:
            maximum = color.new(scale_space, [cs.CHANNELS[0].low] * 3).convert(linear, in_place=True)[0]
        else:
            maximum = color.new(scale_space, [maximum] * 3).convert(linear, in_place=True)[0]
        scale_space = linear

    # Convert to the target gamut
    mapcolor = color.convert(scale_space).normalize(nans=False)

    # Grab the white point and the luminance of the current gamut.
    white = mapcolor._space.WHITE
    Y = mapcolor.luminance()

    # Scale the color into gamut
    rgb = cs.from_base(mapcolor[:-1]) if coerced else mapcolor[:-1]
    mn = min(min(rgb), 0.0) if not clip_negative else 0.0
    mx = max(rgb) - mn
    for i in range(len(rgb)):
        rgb[i] = alg.clamp((rgb[i] - mn) / mx if mx else (rgb[i] - mn), 0.0, 1.0) * maximum
    mapcolor[:-1] = cs.to_base(rgb) if coerced else rgb

    # If the current luminance is greater than the original luminance,
    # set the luminance to the original. Set it xyY with the same white point.
    if not max_saturation:
        adjust_luminance(mapcolor, Y, white)

    # Clip in the original gamut bound color space and update the original color
    clip_channels(mapcolor.convert(orig_space, in_place=True))
    color.update(mapcolor)


def clip_channels(color: Color, nans: bool = True) -> bool:
    """Clip channels."""

    clipped = False

    cs = color._space
    for i, value in enumerate(cs.normalize(color[:-1])):

        chan = cs.channels[i]

        # Ignore angles, undefined, or unbounded channels
        if not chan.bound or chan.flags & FLG_ANGLE or math.isnan(value):
            color[i] = value
            continue

        # Fit value in bounds.
        if value < chan.low:
            color[i] = chan.low
        elif value > chan.high:
            color[i] = chan.high
        else:
            color[i] = value
            continue

        clipped = True

    return clipped


def verify(color: Color, tolerance: float) -> bool:
    """Verify the values are in bound."""

    cs = color._space
    for i, value in enumerate(cs.normalize(color[:-1])):
        chan = cs.channels[i]

        # Ignore undefined channels, angles which wrap, and unbounded channels
        if not chan.bound or math.isnan(value) or chan.flags & FLG_ANGLE:
            continue

        a = chan.low
        b = chan.high

        # Check if bounded values are in bounds
        if (a is not None and value < (a - tolerance)) or (b is not None and value > (b + tolerance)):
            return False
    return True


class Fit(Plugin, metaclass=ABCMeta):
    """Fit plugin class."""

    NAME = ''

    @abstractmethod
    def fit(self, color: Color, space: str, **kwargs: Any) -> None:
        """Get coordinates of the new gamut mapped color."""
