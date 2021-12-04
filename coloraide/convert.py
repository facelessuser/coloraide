"""Convert the color."""
from . import util
from .util import Vector
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color

# XYZ is the absolute base, meaning that XYZ is the final base in any conversion chain.
# This is a design expectation regardless of whether someone assigns a different base to XYZ or not.
ABSOLUTE_BASE = 'xyz-d65'


def convert(color: 'Color', space: str) -> Vector:
    """Convert the color coordinates to the specified space."""

    if color.space() != space:
        obj = color.CS_MAP.get(space)
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))

        # Create a worse case conversion chain from XYZ to the target
        temp = obj
        count = 0
        from_color = []
        from_color_index = {}
        name = ''
        while name != ABSOLUTE_BASE:
            from_color.append(temp)
            name = temp.NAME
            from_color_index[name] = count
            temp = color.CS_MAP[temp.BASE]

            count += 1
            if count > color._MAX_CONVERT_ITERATIONS:  # pragma: no cover
                raise RuntimeError(
                    'Conversion chain reached max size of {} and has terminated to avoid an infinite loop'.format(
                        count
                    )
                )

        # Start converting coordinates until we either match a space in the conversion chain or bottom out at XYZ
        coords = util.no_nans(color.coords())
        current = type(color._space)
        if current.NAME != ABSOLUTE_BASE:
            count = 0
            while current.NAME not in from_color_index:
                # Convert to color's base
                base_space = color.CS_MAP[current.BASE]
                coords = current.to_base(coords)

                # Convert to XYZ, make sure we chromatically adapt to the appropriate white point
                if base_space.NAME == ABSOLUTE_BASE:
                    coords = color.chromatic_adaptation(current.WHITE, base_space.WHITE, coords)

                # Get next color in the chain
                current = base_space

                count += 1
                if count > color._MAX_CONVERT_ITERATIONS:  # pragma: no cover
                    raise RuntimeError(
                        'Conversions reached max iteration of {} and has terminated to avoid an infinite loop'.format(
                            count
                        )
                    )

        # If we still do not match start converting from the point in the conversion chain
        # where are current color resides
        if current.NAME != space:
            start = from_color_index[current.NAME] - 1

            # Convert from XYZ, make sure we chromatically adapt from the appropriate white point
            if current.NAME == ABSOLUTE_BASE:
                coords = color.chromatic_adaptation(current.WHITE, from_color[start].WHITE, coords)

            for index in range(start, -1, -1):
                current = from_color[index]
                coords = current.from_base(coords)

    else:
        # Nothing to convert, just pass values as is
        coords = color.coords()

    return coords
