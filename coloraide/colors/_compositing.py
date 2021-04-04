"""
Compositing and RGB blend modes.

https://www.w3.org/TR/compositing/
"""
from .. import util
import math
from . _range import Angle
from ._gamut import GamutBound
from operator import itemgetter

SUPPORTED = frozenset(
    [
        'normal', 'multiply', 'darken', 'lighten', 'burn', 'dodge', 'screen',
        'overlay', 'hard-light', 'exclusion', 'difference', 'soft-light',
        'hue', 'saturation', 'luminosity', 'color'
    ]
)

NON_SEPARABLE = frozenset(['color', 'hue', 'saturation', 'luminosity'])


def clip_channel(coord, gamut):
    """Clipping channel."""

    a, b = gamut
    is_bound = isinstance(gamut, GamutBound)

    # Wrap the angle. Not technically out of gamut, but we will clean it up.
    if isinstance(a, Angle) and isinstance(b, Angle):
        return coord % 360.0

    # These parameters are unbounded
    if not is_bound:
        # Will not execute unless we have a space that defines some coordinates
        # as bound and others as not. We do not currently have such spaces.
        a = None
        b = None

    # Fit value in bounds.
    return util.clamp(coord, a, b)


def alpha_composite(cb, cs, cba, csa, cra):
    """Overlay one color channel over the other."""

    cr = cs + (cb - cs) * (1 - csa)
    return cr / cra if cra else cr


def lum(rgb):
    """Get luminosity."""

    return 0.3 * rgb[0] + 0.59 * rgb[1] + 0.11 * rgb[2]


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


def handle_nan(cb, cs, cba, csa, cra):
    """Handle `NaN`."""

    cr = None
    if util.is_nan(cs) and util.is_nan(cb):
        cr = 0.0
    elif util.is_nan(cs):
        cr = cb * cba
    elif util.is_nan(cb):
        cr = cs * csa

    if cr is None:
        return cr

    if cra:
        cr /= cra
    return cr


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


def blend_dodge(cb, cs):
    """Blend mode 'dodge'."""

    if cb == 0:
        return 0
    elif cs == 1:
        return 1
    else:
        return min(1, cb / (1 - cs))


def blend_burn(cb, cs):
    """Blend mode 'burn'."""

    if cb == 1:
        return 1
    elif cs == 0:
        return 0
    else:
        return 1 - min(1, (1 - cb) / cs)


def blend_overlay(cb, cs):
    """Blend mode 'overlay'."""

    return blend_screen(cb, 2 * cs - 1) if cb >= 0.5 else blend_multiply(cb, cs * 2)


def blend_difference(cb, cs):
    """Blend mode 'difference'."""

    return abs(cb - cs)


def blend_exclusion(cb, cs):
    """Blend mode 'exclusion'."""

    return cb + cs - 2 * cb * cs


def blend_hard_light(cb, cs):
    """Blend mode 'hard-light'."""

    return blend_multiply(cb, cs * 2) if cs <= 0.5 else blend_screen(cb, 2 * cs - 1)


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


class Compositing:
    """Compositing and blend modes."""

    def blend(self, color, mode, *, space=None, out_space=None):
        """Blend colors using the specified blend mode."""

        # Setup mode.
        mode = mode.lower()
        if mode not in SUPPORTED:
            raise ValueError("'{}' is not a recognized blend mode".format(mode))
        if mode in NON_SEPARABLE:
            space = 'srgb'

        # If we are doing non-separable, we are converting to a special space that
        # can only be done from sRGB, so we have to force sRGB anyway.
        space = self.space() if space is None else space.lower()
        outspace = self.space() if out_space is None else out_space.lower()

        # Convert and fit to the color space.
        color1 = self.convert(space, fit=True)
        color2 = color.convert(space, fit=True)

        # Calculate the result alpha
        cba = util.no_nan(color2.alpha)
        csa = util.no_nan(color1.alpha)
        cra = csa + cba * (1.0 - csa)

        gamut = color1._range
        coords = []
        blender = globals()['blend_{}'.format(mode.replace('-', '_'))]
        if mode not in NON_SEPARABLE:
            # Blend each channel. Afterward, clip and apply alpha compositing.
            i = 0
            for cb, cs in zip(color2.coords(), color1.coords()):
                cr = handle_nan(cb, cs, cba, csa, cra)
                if cr is not None:
                    coords.append(clip_channel(cr, gamut[i]))
                else:
                    cr = clip_channel(blender(cb, cs), gamut[i])
                    coords.append(alpha_composite(cb, cr, cba, csa, cra))
                i += 1
        else:
            # Convert to a hue, saturation, luminosity space and apply the requested blending.
            # Afterwards, clip and apply alpha compositing.
            i = 0
            for cb, cr in zip(color2.coords(), blender(util.no_nan(color2.coords()), util.no_nan(color1.coords()))):
                cr = clip_channel(cr, gamut[i])
                coords.append(alpha_composite(cb, cr, cba, csa, cra))
                i += 1

        color1.update(coords, cra)
        return color1.convert(outspace)

    def composite(self, background, *, space=None, out_space=None):
        """
        Apply the given transparency with the given background.

        This attempts to give a color that represents what the eye
        sees with the transparent color against the given background.

        If using a Cylindrical space, hue will not be overlaid, instead it
        will just be interpolated.
        """

        return self.blend(background, "normal", space=space, out_space=out_space)

    @util.deprecated("'overlay' is deprecated, 'composite should be used instead'.")
    def overlay(self, *args, **kwargs):
        """Alpha compositing."""

        return self.composite(*args, **kwargs)
