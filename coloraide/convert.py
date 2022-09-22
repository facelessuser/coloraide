"""Convert the color."""
from __future__ import annotations
from . import algebra as alg
from .types import Vector
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color
    from .spaces import Space

# XYZ is the absolute base, meaning that XYZ is the final base in any conversion chain.
# This is a design expectation regardless of whether someone assigns a different base to XYZ or not.
ABSOLUTE_BASE = 'xyz-d65'


def calc_path_to_xyz(
    color: type[Color],
    space: str
) -> tuple[list[Space], dict[str, int]]:
    """
    Calculate the conversion path between a given color space and XYZ D65.

    We create two structures:

    1. A list containing the color space name in the conversion process from our target to XYZ D65.
    2. A mapping of color space names to the index in the color space name list.
    """

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

    return from_color, from_color_index


def get_convert_chain(
    color: type[Color],
    space: Space,
    target: str
) -> list[tuple[Space, Space, int, bool]]:
    """
    Create a conversion chain.

    Each entry in the list will contain (from_space, to_space, direction, chromatic_adaptation_needed).
    Direction refers to whether conversions are moving to or from XYZ D65 as that will dictate whether
    `to_base` or `from_base` call method is used. If either the "from" or "to" color space is XYZ D65
    a chromatic adaptation will need to occur.
    """

    # Get the color space chain for the current space to XYZ
    from_color, from_color_index = calc_path_to_xyz(color, target)

    # Start building up the conversion chain.
    # The first stage builds up the chain towards XYZ D65.
    # If the color space we are converting to is not between
    # the current space and XYZ D65, nothing will get added.
    current = space
    chain = []  # type: list[tuple[Space, Space, int, bool]]
    if current.NAME != ABSOLUTE_BASE:
        count = 0
        while current.NAME not in from_color_index:

            # Get the "base space" (the space through which the current color converts to and from)
            base_space = color.CS_MAP[current.BASE]

            # Do we need to chromatically adapt towards XYZ D65?
            adapt = base_space.NAME == ABSOLUTE_BASE

            # Add conversion chain entry
            chain.append((current, base_space, 0, adapt))

            # The base space is now the current space
            current = base_space

            count += 1
            if count > color._MAX_CONVERT_ITERATIONS:  # pragma: no cover
                raise RuntimeError(
                    'Conversions reached max iteration of {} and has terminated to avoid an infinite loop'.format(
                        count
                    )
                )

    # If the chain still didn't resolve to the target space after the first stage,
    # build up the chain in the direction away from XYZ-D65.
    if current.NAME != target:
        # Start in the chain where the current color resides
        start = from_color_index[current.NAME] - 1

        # Do we need to chromatically adapt away from XYZ D65?
        adapt = current.NAME == ABSOLUTE_BASE

        # Moving away from XYZ D65, convert towards are desired target
        for index in range(start, -1, -1):
            base_space = current
            current = from_color[index]

            # Add the conversion chain entry
            chain.append((base_space, current, 1, adapt))

    return chain


def convert(color: Color, space: str) -> tuple[Space, Vector]:
    """Convert the color coordinates to the specified space."""

    # Grab the convert for the current space to the desired space
    # Result is cached for quicker future conversions.
    chain = color._get_convert_chain(color._space, space)  # type: ignore[attr-defined]

    # Get coordinates and convert NaN values to 0
    coords = alg.no_nans(color[:-1])

    # Navigate the conversion chain translated the coordinates along the way.
    # Perform chromatic adaption if needed (a conversion to or from XYZ D65).
    last = color._space
    for a, b, direction, adapt in chain:
        if direction and adapt:
            coords = color.chromatic_adaptation(
                a.WHITE,
                b.WHITE,
                coords
            )

        coords = b.from_base(coords) if direction else a.to_base(coords)
        if not direction and adapt:
            coords = color.chromatic_adaptation(
                a.WHITE,
                b.WHITE,
                coords
            )
        last = b

    return last, coords
