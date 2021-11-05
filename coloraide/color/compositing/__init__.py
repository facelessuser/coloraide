"""
Compositing and RGB blend modes.

https://www.w3.org/TR/compositing/
"""
from . import porter_duff
from . import blend_modes
from ... import util
from ...util import MutableVector
from ...spaces import GamutBound
from typing import Tuple, Optional, Union, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ...color import Color


def clip_channel(coord: float, gamut: Tuple[float, ...]) -> float:
    """Clipping channel."""

    a = gamut[0]  # type: Optional[float]
    b = gamut[1]  # type: Optional[float]
    is_bound = isinstance(gamut, GamutBound)

    # These parameters are unbounded
    if not is_bound:  # pragma: no cover
        # Will not execute unless we have a space that defines some coordinates
        # as bound and others as not. We do not currently have such spaces.
        a = None
        b = None

    # Fit value in bounds.
    return util.clamp(coord, a, b)


def compose(
    color1: 'Color',
    color2: 'Color',
    blend: Union[str, bool],
    operator: Union[str, bool],
    non_seperable: bool
) -> 'Color':
    """Blend colors using the specified blend mode."""

    # Get the color coordinates
    csa = util.no_nan(color1.alpha)
    cba = util.no_nan(color2.alpha)
    coords1 = util.no_nans(color1.coords())
    coords2 = util.no_nans(color2.coords())

    # Setup compositing
    compositor = None  # type: Optional[porter_duff.PorterDuff]
    cra = csa
    if isinstance(operator, str):
        compositor = porter_duff.compositor(operator)(cba, csa)
        cra = compositor.ao()
    elif operator is True:
        compositor = porter_duff.compositor('source-over')(cba, csa)
        cra = compositor.ao()

    # Perform compositing
    gamut = color1._space.RANGE
    coords = []  # type: MutableVector
    if isinstance(blend, str) and non_seperable:
        # Setup blend mode.
        ns_blender = blend_modes.get_non_seperable_blender(blend.lower())

        # Convert to a hue, saturation, luminosity space and apply the requested blending.
        # Afterwards, clip and apply alpha compositing.
        i = 0
        blended = ns_blender(coords2, coords1) if ns_blender is not None else coords1
        for cb, cr in zip(coords2, blended):
            cr = (1 - cba) * cr + cba * cr if ns_blender is not None else cr
            cr = clip_channel(cr, gamut[i])
            coords.append(compositor.co(cb, cr) if compositor is not None else cr)
            i += 1
    else:
        # Setup blend mode.
        blender = None  # type: Optional[Callable[[float, float], float]]
        if isinstance(blend, str):
            blend = blend.lower()
            blender = blend_modes.get_seperable_blender(blend)
        elif blend is True:
            blender = blend_modes.get_seperable_blender('normal')

        # Blend each channel. Afterward, clip and apply alpha compositing.
        i = 0
        for cb, cs in zip(coords2, coords1):
            cr = (1 - cba) * cs + cba * blender(cb, cs) if blender is not None else cs
            cr = clip_channel(cr, gamut[i])
            coords.append(compositor.co(cb, cr) if compositor is not None else cr)
            i += 1

    return color1.update(color1.space(), coords, cra)
