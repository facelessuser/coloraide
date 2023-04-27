"""Average colors together."""
from __future__ import annotations
import math
from .types import ColorInput, Vector
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color


def premultiply(coords: Vector, hue_index: int) -> Vector:
    """Premultiply the color before averaging."""

    alpha = coords[-1]

    if math.isnan(alpha) or alpha == 1.0:
        return coords

    for i in range(len(coords) - 1):
        if i != hue_index:
            coords[i] *= alpha

    return coords


def postdivide(coords: Vector, hue_index: int) -> Vector:
    """Undo premultiplication of semi-transparent colors."""

    alpha = coords[-1]

    if math.isnan(alpha) or alpha in (0.0, 1.0):
        return coords

    for i in range(len(coords) - 1):
        if i != hue_index:
            coords[i] /= alpha

    return coords


def average(create: type[Color], colors: Iterable[ColorInput], space: str, premultiplied: bool = True) -> Color:
    """Average a list of colors together."""

    obj = create(space, [])

    # Get channel information
    cs = obj.CS_MAP[space]
    hue_index = cs.hue_index() if hasattr(cs, 'hue_index') else -1
    channels = cs.channels
    chan_count = len(channels)
    sums = [0.0] * chan_count
    totals = [0.0] * chan_count
    sin = 0.0
    cos = 0.0

    # Sum channel values
    e = -1
    for e, c in enumerate(colors):
        coords = premultiply(obj.update(c)[:], hue_index) if premultiplied else obj.update(c)[:]
        for e, coord in enumerate(coords):
            if math.isnan(coord):
                continue
            totals[e] += 1
            if e == hue_index:
                rad = math.radians(coord)
                sin += math.sin(rad)
                cos += math.cos(rad)
            else:
                sums[e] += coord

    if e == -1:
        raise ValueError('At least one color must be provided in order to average colors')

    # Get the mean
    for e, total in enumerate(totals):
        if not total:
            sums[e] = float('nan')
        elif e == hue_index:
            sums[e] = math.degrees(math.atan2(sin / total, cos / total))
        else:
            sums[e] /= total

    # Undo premultiplication
    if premultiplied:
        sums = postdivide(sums, hue_index)

    # Return the color
    return obj.update(space, sums[:-1], sums[-1])
