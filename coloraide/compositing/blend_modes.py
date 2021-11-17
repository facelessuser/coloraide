"""Blend modes."""
import math
from operator import itemgetter
from typing import Any, Callable, cast
from ..util import Vector, MutableVector


def is_non_seperable(mode: Any) -> bool:
    """Check if blend mode is non-separable."""

    return mode in frozenset(['color', 'hue', 'saturation', 'luminosity'])


# -----------------------------------------
# Non-separable blending helper functions
# -----------------------------------------
def lum(rgb: Vector) -> float:
    """Get luminosity."""

    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def clip_color(rgb: MutableVector) -> MutableVector:
    """Clip color."""

    l = lum(rgb)
    n = min(*rgb)
    x = max(*rgb)

    if n < 0:
        rgb = [l + (((c - l) * l) / (l - n)) for c in rgb]

    if x > 1:
        rgb = [l + (((c - l) * (1 - l)) / (x - l)) for c in rgb]

    return rgb


def set_lum(rgb: Vector, l: float) -> MutableVector:
    """Set luminosity."""

    d = l - lum(rgb)
    new_rgb = [c + d for c in rgb]
    return clip_color(new_rgb)


def sat(rgb: Vector) -> float:
    """Saturation."""

    return max(*rgb) - min(*rgb)


def set_sat(rgb: Vector, s: float) -> MutableVector:
    """Set saturation."""

    final = [0.0] * 3
    indices, rgb = zip(*sorted(enumerate(rgb), key=itemgetter(1)))
    if rgb[2] > rgb[0]:
        final[indices[1]] = (((rgb[1] - rgb[0]) * s) / (rgb[2] - rgb[0]))
        final[indices[2]] = s
    else:
        final[indices[1]] = 0
        final[indices[2]] = 0
    final[indices[0]] = 0
    return final


# -----------------------------------------
# Blend modes
# -----------------------------------------
def blend_normal(cb: float, cs: float) -> float:
    """Blend mode 'normal'."""

    return cs


def blend_multiply(cb: float, cs: float) -> float:
    """Blend mode 'multiply'."""

    return cb * cs


def blend_screen(cb: float, cs: float) -> float:
    """Blend mode 'screen'."""

    return cb + cs - (cb * cs)


def blend_darken(cb: float, cs: float) -> float:
    """Blend mode 'darken'."""

    return min(cb, cs)


def blend_lighten(cb: float, cs: float) -> float:
    """Blend mode 'lighten'."""

    return max(cb, cs)


def blend_color_dodge(cb: float, cs: float) -> float:
    """Blend mode 'dodge'."""

    if cb == 0:
        return 0
    elif cs == 1:
        return 1
    else:
        return min(1, cb / (1 - cs))


def blend_color_burn(cb: float, cs: float) -> float:
    """Blend mode 'burn'."""

    if cb == 1:
        return 1
    elif cs == 0:
        return 0
    else:
        return 1 - min(1, (1 - cb) / cs)


def blend_overlay(cb: float, cs: float) -> float:
    """Blend mode 'overlay'."""

    if cb >= 0.5:
        return blend_screen(cb, 2 * cs - 1)
    else:
        return blend_multiply(cb, cs * 2)


def blend_difference(cb: float, cs: float) -> float:
    """Blend mode 'difference'."""

    return abs(cb - cs)


def blend_exclusion(cb: float, cs: float) -> float:
    """Blend mode 'exclusion'."""

    return cb + cs - 2 * cb * cs


def blend_hard_light(cb: float, cs: float) -> float:
    """Blend mode 'hard-light'."""

    if cs <= 0.5:
        return blend_multiply(cb, cs * 2)
    else:
        return blend_screen(cb, 2 * cs - 1)


def blend_soft_light(cb: float, cs: float) -> float:
    """Blend mode 'soft-light'."""

    if cs <= 0.5:
        return cb - (1 - 2 * cs) * cb * (1 - cb)
    else:
        if cb <= 0.25:
            d = ((16 * cb - 12) * cb + 4) * cb
        else:
            d = math.sqrt(cb)
        return cb + (2 * cs - 1) * (d - cb)


def non_seperable_blend_hue(cb: Vector, cs: Vector) -> MutableVector:
    """Blend mode 'hue'."""

    return set_lum(set_sat(cs, sat(cb)), lum(cb))


def non_seperable_blend_saturation(cb: Vector, cs: Vector) -> MutableVector:
    """Blend mode 'saturation'."""

    return set_lum(set_sat(cb, sat(cs)), lum(cb))


def non_seperable_blend_luminosity(cb: Vector, cs: Vector) -> MutableVector:
    """Blend mode 'luminosity'."""
    return set_lum(cb, lum(cs))


def non_seperable_blend_color(cb: Vector, cs: Vector) -> MutableVector:
    """Blend mode 'color'."""

    return set_lum(cs, lum(cb))


def get_seperable_blender(blend: str) -> Callable[[float, float], float]:
    """Get desired blend mode."""

    try:
        return cast(
            Callable[[float, float], float],
            globals()['blend_{}'.format(blend.replace('-', '_'))]
        )
    except KeyError:
        raise ValueError("'{}' is not a recognized blend mode".format(blend))


def get_non_seperable_blender(blend: str) -> Callable[[Vector, Vector], Vector]:
    """Get desired blend mode."""

    try:
        return cast(
            Callable[[Vector, Vector], Vector],
            globals()['non_seperable_blend_{}'.format(blend.replace('-', '_'))]
        )
    except KeyError:  # pragma: no cover
        # The way we use this function, we will never hit this as we've verified the method before calling
        raise ValueError("'{}' is not a recognized non seperable blend mode".format(blend))
