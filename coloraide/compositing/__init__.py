"""
Compositing and RGB blend modes.

https://www.w3.org/TR/compositing/
"""
from __future__ import annotations
from .. spaces import RGBish
from . import porter_duff
from . import blend_modes
from .. import algebra as alg
from ..channels import Channel
from ..types import Vector, ColorInput, AnyColor
from typing import Sequence


def clip_channel(coord: float, channel: Channel) -> float:
    """Clipping channel."""

    if channel.bound:
        a = channel.low  # type: float | None
        b = channel.high  # type: float | None

    # These parameters are unbounded
    else:  # pragma: no cover
        # Will not execute unless we have a space that defines some coordinates
        # as bound and others as not. We do not currently have such spaces.
        a = None
        b = None

    # Fit value in bounds.
    return alg.clamp(coord, a, b)


def apply_compositing(
    color1: Vector,
    color2: Vector,
    channels: tuple[Channel, ...],
    blender: blend_modes.Blend | None,
    operator: str | bool
) -> Vector:
    """Perform the actual blending."""

    # Get the color coordinates
    csa = color1[-1]
    cba = color2[-1]
    coords1 = color1[:-1]
    coords2 = color2[:-1]

    # Setup compositing
    compositor = None  # type: porter_duff.PorterDuff | None
    cra = csa
    if isinstance(operator, str):
        compositor = porter_duff.compositor(operator)(cba, csa)
        cra = alg.clamp(compositor.ao(), 0, 1)
    elif operator is True:
        compositor = porter_duff.compositor('source-over')(cba, csa)
        cra = alg.clamp(compositor.ao(), 0, 1)

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
    color_cls: type[AnyColor],
    colors: Sequence[ColorInput],
    blend: str | bool = True,
    operator: str | bool = True,
    space: str | None = None,
    out_space: str | None = None
) -> AnyColor:
    """Blend colors using the specified blend mode."""

    if not colors:  # pragma: no cover
        raise ValueError('At least one color is required for compositing.')

    # We need to go ahead and grab the blender as we need to check what type of blender it is.
    blender = None  # blend_modes.Blend | None
    if isinstance(blend, str):
        blender = blend_modes.get_blender(blend)
    elif blend is True:
        blender = blend_modes.get_blender('normal')

    # If we are doing non-separable, we are converting to a special space that
    # can only be done from sRGB, so we have to force sRGB anyway.
    if space is None:
        space = 'srgb'
    if out_space is None:
        out_space = space

    if not isinstance(color_cls.CS_MAP[space], RGBish):
        raise ValueError(f"Can only compose in an RGBish color space, not {type(color_cls.CS_MAP[space])}")

    dest = color_cls._handle_color_input(colors[-1]).convert(space).normalize(nans=False)[:]
    for x in range(len(colors) - 2, -1, -1):
        src = color_cls._handle_color_input(colors[x]).convert(space).normalize(nans=False)[:]
        dest = apply_compositing(src, dest, color_cls.CS_MAP[space].channels, blender, operator)

    return color_cls(space, dest[:-1], dest[-1]).convert(out_space, in_place=True)
