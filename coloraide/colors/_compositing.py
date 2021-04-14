"""
Compositing and RGB blend modes.

https://www.w3.org/TR/compositing/
"""
import math
from .. import util
from ._gamut import GamutBound
from operator import itemgetter
from collections.abc import Sequence
from . import _porter_duff as pd

SUPPORTED = frozenset(
    [
        'normal', 'multiply', 'darken', 'lighten', 'color-burn', 'color-dodge', 'screen',
        'overlay', 'hard-light', 'exclusion', 'difference', 'soft-light',
        'hue', 'saturation', 'luminosity', 'color'
    ]
)

NON_SEPARABLE = frozenset(['color', 'hue', 'saturation', 'luminosity'])


# -----------------------------------------
# Non-separable blending helper functions
# -----------------------------------------
def clip_channel(coord, gamut):
    """Clipping channel."""

    a, b = gamut
    is_bound = isinstance(gamut, GamutBound)

    # These parameters are unbounded
    if not is_bound:  # pragma: no cover
        # Will not execute unless we have a space that defines some coordinates
        # as bound and others as not. We do not currently have such spaces.
        a = None
        b = None

    # Fit value in bounds.
    return util.clamp(coord, a, b)


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


def compose(color1, color2, blend, operator, non_seperable):
    """Blend colors using the specified blend mode."""

    # Get the color coordinates
    csa = util.no_nan(color1.alpha)
    cba = util.no_nan(color2.alpha)
    coords1 = util.no_nan(color1.coords())
    coords2 = util.no_nan(color2.coords())

    # Setup blend mode.
    if blend is None:
        blend = 'normal'
    if blend is not False:
        blend = blend.lower()
        if blend not in SUPPORTED:
            raise ValueError("'{}' is not a recognized blend mode".format(blend))
        blender = globals()['blend_{}'.format(blend.replace('-', '_'))]
    else:
        blender = None

    # Setup compositing
    if operator is None:
        operator = 'source-over'
    if operator is not False:
        compositor = pd.compositor(operator)(cba, csa)
        cra = compositor.ao()
    else:
        cra = csa
        compositor = None

    # Perform compositing
    gamut = color1._range
    coords = []
    if not non_seperable:
        # Blend each channel. Afterward, clip and apply alpha compositing.
        i = 0
        for cb, cs in zip(coords2, coords1):
            cr = (1 - cba) * cs + cba * blender(cb, cs) if blender is not None else cs
            cr = clip_channel(cr, gamut[i])
            coords.append(compositor.co(cb, cr) if compositor is not None else cr)
            i += 1
    else:
        # Convert to a hue, saturation, luminosity space and apply the requested blending.
        # Afterwards, clip and apply alpha compositing.
        i = 0
        blended = blender(coords2, coords1) if blender is not None else coords1
        for cb, cr in zip(coords2, blended):
            cr = (1 - cba) * cr + cba * cr if blender is not None else cr
            cr = clip_channel(cr, gamut[i])
            coords.append(compositor.co(cb, cr) if compositor is not None else cr)
            i += 1

    return color1.update(coords, cra)


class Compositing:
    """Compositing and blend modes."""

    def compose(self, backdrop, *, blend=None, operator=None, space=None, out_space=None):
        """Blend colors using the specified blend mode."""

        # If we are doing non-separable, we are converting to a special space that
        # can only be done from sRGB, so we have to force sRGB anyway.
        non_seperable = blend in NON_SEPARABLE
        if non_seperable:
            space = 'srgb'
        space = 'srgb' if space is None else space.lower()
        outspace = self.space() if out_space is None else out_space.lower()

        if not isinstance(backdrop, Sequence):
            backdrop = [backdrop]

        if len(backdrop) == 0:
            return self.convert(outspace)

        if len(backdrop) > 1:
            dest = backdrop[-1].convert(space, fit=True)
            for x in range(len(backdrop) - 2, -1, -1):
                src = backdrop[x].convert(space, fit=True)
                dest = compose(src, dest, blend, operator, non_seperable)
        else:
            dest = backdrop[0].convert(space, fit=True)

        src = self.convert(space, fit=True)
        dest = compose(src, dest, blend, operator, non_seperable)

        return dest.convert(outspace)
