"""Average colors together."""
from __future__ import annotations
import math
from .types import ColorInput
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color


def average(create: type[Color], colors: Iterable[ColorInput], space: str, premultiplied: bool = True) -> Color:
    """Average a list of colors together."""

    obj = create(space, [])

    # Get channel information
    cs = obj.CS_MAP[space]
    hue_index = cs.hue_index() if hasattr(cs, 'hue_index') else -1
    channels = cs.channels
    chan_count = len(channels)
    alpha_index = chan_count - 1
    sums = [0.0] * chan_count
    totals = [0.0] * chan_count
    sin = 0.0
    cos = 0.0

    # Sum channel values
    i = -1
    for c in colors:
        coords = obj.update(c)[:]
        alpha = coords[-1]
        if math.isnan(alpha):
            alpha = 1.0
        i = 0
        for coord in coords:
            if not math.isnan(coord):
                totals[i] += 1
                if i == hue_index:
                    rad = math.radians(coord)
                    sin += math.sin(rad)
                    cos += math.cos(rad)
                else:
                    sums[i] += (coord * alpha) if premultiplied and i != alpha_index else coord
            i += 1

    if i == -1:
        raise ValueError('At least one color must be provided in order to average colors')

    # Get the mean
    alpha = sums[-1]
    alpha_t = totals[-1]
    sums[-1] = float('nan') if not alpha_t else alpha / alpha_t
    alpha = sums[-1]
    if math.isnan(alpha) or alpha in (0.0, 1.0):
        alpha = 1.0
    for i in range(chan_count - 1):
        total = totals[i]
        if not total:
            sums[i] = float('nan')
        elif i == hue_index:
            sums[i] = math.degrees(math.atan2(sin / total, cos / total))
        else:
            sums[i] /= total * alpha if premultiplied else total

    # Return the color
    return obj.update(space, sums[:-1], sums[-1])
