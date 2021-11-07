"""Convert the color."""
from .. import util
from ..util import Vector
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def convert(color: 'Color', space: str) -> Vector:
    """Convert the color coordinates to the specified space."""

    if color.space() != space:
        convert_to = '_to_{}'.format(space.replace('-', '_'))
        convert_from = '_from_{}'.format(color.space().replace('-', '_'))

        obj = color.CS_MAP.get(space)
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))

        # See if there is a direct conversion route
        func = None
        # Don't send NaNs
        coords = util.no_nans(color.coords())
        if hasattr(color._space, convert_to):
            func = getattr(color._space, convert_to)
            coords = func(color, coords)
        elif hasattr(obj, convert_from):
            func = getattr(obj, convert_from)
            coords = func(color, coords)

        # See if there is an XYZ route
        if func is None and color.space() != space:
            func = getattr(color._space, '_to_xyz')
            coords = func(color, coords)

            if space != 'xyz':
                func = getattr(obj, '_from_xyz')
                coords = func(color, coords)
    else:
        # Nothing to convert, just pass values as is
        coords = color.coords()

    return coords
