"""
Compositing and RGB blend modes.

https://www.w3.org/TR/compositing/
"""
from collections.abc import Sequence
from . import porter_duff
from . import blend_modes
from ... import util
from ...spaces import GamutBound


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
        blender = blend_modes.get_blender(blend)
    else:
        blender = None

    # Setup compositing
    if operator is None:
        operator = 'source-over'
    if operator is not False:
        compositor = porter_duff.compositor(operator)(cba, csa)
        cra = compositor.ao()
    else:
        cra = csa
        compositor = None

    # Perform compositing
    gamut = color1._space.RANGE
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

    return color1.update(color1.space(), coords, cra)


class Compose:
    """Handle compositing."""

    def compose(self, backdrop, *, blend=None, operator=None, space=None, out_space=None, in_place=False):
        """Blend colors using the specified blend mode."""

        backdrop = self._handle_color_input(backdrop, sequence=True)

        # If we are doing non-separable, we are converting to a special space that
        # can only be done from sRGB, so we have to force sRGB anyway.
        non_seperable = blend_modes.is_non_seperable(blend)
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

        return self.mutate(dest.convert(outspace)) if in_place else dest.convert(outspace)

    @util.deprecated("'overlay' is deprecated, 'compose' should be used instead.")
    def overlay(self, backdrop, *, space=None, in_place=False):
        """Redirect to compose."""

        if space is None:
            space = self.space()
        return self.compose(backdrop, space=space, out_space=None, in_place=in_place)
