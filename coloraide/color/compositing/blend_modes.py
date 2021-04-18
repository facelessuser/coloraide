"""Blend modes."""
import math
from operator import itemgetter

SUPPORTED = frozenset(
    [
        'normal', 'multiply', 'darken', 'lighten', 'color-burn', 'color-dodge', 'screen',
        'overlay', 'hard-light', 'exclusion', 'difference', 'soft-light',
        'hue', 'saturation', 'luminosity', 'color'
    ]
)

NON_SEPARABLE = frozenset(['color', 'hue', 'saturation', 'luminosity'])


def is_non_seperable(mode):
    """Check if blend mode is non-separable."""

    return mode in frozenset(['color', 'hue', 'saturation', 'luminosity'])


# -----------------------------------------
# Non-separable blending helper functions
# -----------------------------------------
def lum(rgb):
    """Get luminosity."""

    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def clip_color(rgb):
    """Clip color."""

    l = lum(rgb)
    n = min(*rgb)
    x = max(*rgb)
    if n < 0:
        rgb = [l + (((c - l) * l) / (l - n)) for c in rgb]

    if x > 1:
        rgb = [l + (((c - l) * (1 - l)) / (x - l)) for c in rgb]

    return rgb


def set_lum(rgb, l):
    """Set luminosity."""

    d = l - lum(rgb)
    rgb = [c + d for c in rgb]
    return clip_color(rgb)


def sat(rgb):
    """Saturation."""

    return max(*rgb) - min(*rgb)


def set_sat(rgb, s):
    """Set saturation."""

    final = [0] * 3
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
def blend_normal(cb, cs):
    """Blend mode 'normal'."""

    return cs


def blend_multiply(cb, cs):
    """Blend mode 'multiply'."""

    return cb * cs


def blend_screen(cb, cs):
    """Blend mode 'screen'."""

    return cb + cs - (cb * cs)


def blend_darken(cb, cs):
    """Blend mode 'darken'."""

    return min(cb, cs)


def blend_lighten(cb, cs):
    """Blend mode 'lighten'."""

    return max(cb, cs)


def blend_color_dodge(cb, cs):
    """Blend mode 'dodge'."""

    if cb == 0:
        return 0
    elif cs == 1:
        return 1
    else:
        return min(1, cb / (1 - cs))


def blend_color_burn(cb, cs):
    """Blend mode 'burn'."""

    if cb == 1:
        return 1
    elif cs == 0:
        return 0
    else:
        return 1 - min(1, (1 - cb) / cs)


def blend_overlay(cb, cs):
    """Blend mode 'overlay'."""

    if cb >= 0.5:
        return blend_screen(cb, 2 * cs - 1)
    else:
        return blend_multiply(cb, cs * 2)


def blend_difference(cb, cs):
    """Blend mode 'difference'."""

    return abs(cb - cs)


def blend_exclusion(cb, cs):
    """Blend mode 'exclusion'."""

    return cb + cs - 2 * cb * cs


def blend_hard_light(cb, cs):
    """Blend mode 'hard-light'."""

    if cs <= 0.5:
        return blend_multiply(cb, cs * 2)
    else:
        return blend_screen(cb, 2 * cs - 1)


def blend_soft_light(cb, cs):
    """Blend mode 'soft-light'."""

    if cs <= 0.5:
        return cb - (1 - 2 * cs) * cb * (1 - cb)
    else:
        if cb <= 0.25:
            d = ((16 * cb - 12) * cb + 4) * cb
        else:
            d = math.sqrt(cb)
        return cb + (2 * cs - 1) * (d - cb)


def blend_hue(cb, cs):
    """Blend mode 'hue'."""

    return set_lum(set_sat(cs, sat(cb)), lum(cb))


def blend_saturation(cb, cs):
    """Blend mode 'saturation'."""

    return set_lum(set_sat(cb, sat(cs)), lum(cb))


def blend_luminosity(cb, cs):
    """Blend mode 'luminosity'."""
    return set_lum(cb, lum(cs))


def blend_color(cb, cs):
    """Blend mode 'color'."""

    return set_lum(cs, lum(cb))


def get_blender(blend):
    """Get desired blend mode."""

    if blend not in SUPPORTED:
        raise ValueError("'{}' is not a recognized blend mode".format(blend))
    return globals()['blend_{}'.format(blend.replace('-', '_'))]
