"""Average colors together."""
from __future__ import annotations
import math
from .types import ColorInput, Vector
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color


def premultiply(color: Color, hue_index: int, enabled: bool) -> tuple[Vector, float]:
    """Premultiply the color before averaging."""

    alpha = color.alpha()
    # alphas.append(alpha)

    if not enabled or math.isnan(alpha) or alpha == 1.0:
        return color.coords(), alpha

    return [c if e == hue_index else c * alpha for e, c in enumerate(color.coords())], alpha


def postdivide(coords: Vector, hue_index: int) -> Vector:
    """Undo premultiplication of semi-transparent colors."""

    alpha = coords[-1]

    if math.isnan(alpha) or alpha in (0.0, 1.0):
        return coords

    for i, value in enumerate(coords[:-1]):

        if i == hue_index:
            continue

        coords[i] = value / alpha

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
        coords, alpha = premultiply(obj.new(c).convert(space, in_place=True), hue_index, premultiplied)
        if not math.isnan(alpha):
            sums[-1] += alpha
            totals[-1] += 1

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
    for i in range(chan_count):
        total = totals[i]
        if not total:
            sums[i] == float('nan')
        elif i == hue_index:
            sums[i] = math.degrees(math.atan2(sin / total, cos / total))
        else:
            sums[i] = sums[i] / total

    # Undo premultiplication
    if premultiplied:
        sums = postdivide(sums, hue_index)

    # Return the color
    return obj.update(space, sums[:-1], sums[-1])
