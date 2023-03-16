"""
Compositing and RGB blend modes.

https://www.w3.org/TR/compositing/
"""
from __future__ import annotations
from . import porter_duff
from . import blend_modes
from .. import algebra as alg
from ..channels import Channel
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def clip_channel(coord: float, channel: Channel) -> float:
    """Clipping channel."""

    a = channel.low  # type: float | None
    b = channel.high  # type: float | None

    # These parameters are unbounded
    if not channel.bound:  # pragma: no cover
        # Will not execute unless we have a space that defines some coordinates
        # as bound and others as not. We do not currently have such spaces.
        a = None
        b = None

    # Fit value in bounds.
    return alg.clamp(coord, a, b)


def apply_compositing(
    color1: Color,
    color2: Color,
    blender: blend_modes.Blend | None,
    operator: str | bool
) -> Color:
    """Perform the actual blending."""

    # Get the color coordinates
    csa = color1.alpha(undef=False)
    cba = color2.alpha(undef=False)
    coords1 = color1.coords(undef=False)
    coords2 = color2.coords(undef=False)

    # Setup compositing
    compositor = None  # type: porter_duff.PorterDuff | None
    cra = csa
    if isinstance(operator, str):
        compositor = porter_duff.compositor(operator)(cba, csa)
        cra = alg.clamp(compositor.ao(), 0, 1)
    elif operator is True:
        compositor = porter_duff.compositor('source-over')(cba, csa)
        cra = alg.clamp(compositor.ao(), 0, 1)

    # Perform compositing
    channels = color1._space.CHANNELS

    # Blend each channel. Afterward, clip and apply alpha compositing.
    i = 0
    for cb, cr in zip(coords2, blender.blend(coords2, coords1) if blender else coords1):
        cr = clip_channel(cr, channels[i])
        if compositor:
            color1[i] = compositor.co(cb, cr)
            if cra not in (0, 1):
                color1[i] /= cra
        else:
            color1[i] = cr
        i += 1

    color1[-1] = cra
    return color1


def compose(
    color: Color,
    backdrop: list[Color],
    blend: str | bool = True,
    operator: str | bool = True,
    space: str | None = None
) -> Color:
    """Blend colors using the specified blend mode."""

    # We need to go ahead and grab the blender as we need to check what type of blender it is.
    blender = None  # blend_modes.Blend | None
    if isinstance(blend, str):
        blender = blend_modes.get_blender(blend)
    elif blend is True:
        blender = blend_modes.get_blender('normal')
    is_seperable = blender is not None and isinstance(blender, blend_modes.NonSeperableBlend)

    # If we are doing non-separable, we are converting to a special space that
    # can only be done from sRGB, so we have to force sRGB anyway.
    if space is None or is_seperable:
        space = 'srgb'

    if not backdrop:
        return color

    if len(backdrop) > 1:
        dest = backdrop[-1].convert(space)
        for x in range(len(backdrop) - 2, -1, -1):
            src = backdrop[x].convert(space)
            dest = apply_compositing(src, dest, blender, operator)
    else:
        dest = backdrop[0].convert(space)

    src = color.convert(space)

    return apply_compositing(src, dest, blender, operator)
