"""Average colors together."""
from __future__ import annotations
import math
from .spaces import HWBish
from .types import ColorInput
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color


ACHROMATIC_THRESHOLD = 1e-4


def average(
    color_cls: type[Color],
    colors: Iterable[ColorInput],
    space: str,
    premultiplied: bool = True
) -> Color:
    """
    Average a list of colors together.

    Polar coordinates use a circular mean: https://en.wikipedia.org/wiki/Circular_mean.
    """

    obj = color_cls(space, [])

    # Get channel information
    cs = obj.CS_MAP[space]
    if cs.is_polar():
        hue_index = cs.hue_index()  # type: ignore[attr-defined]
        is_hwb = isinstance(cs, HWBish)
    else:
        hue_index = -1
        is_hwb = False
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
        obj.update(c)
        # If cylindrical color is achromatic, ensure hue is undefined
        if hue_index >= 0 and not math.isnan(obj[hue_index]) and obj.is_achromatic():
            obj[hue_index] = math.nan
        coords = obj[:]
        alpha = coords[-1]
        if math.isnan(alpha):
            alpha = 1.0
        i = 0
        for coord in coords:
            # No need to average an undefined value or color components if alpha is zero
            if not math.isnan(coord) and (premultiplied or alpha or i == alpha_index):
                totals[i] += 1
                if i == hue_index:
                    rad = math.radians(coord)
                    if premultiplied:
                        sin += math.sin(rad) * alpha
                        cos += math.cos(rad) * alpha
                    else:
                        sin += math.sin(rad)
                        cos += math.cos(rad)
                else:
                    sums[i] += (coord * alpha) if premultiplied and i != alpha_index else coord
            i += 1

    if i == -1:
        raise ValueError('At least one color must be provided in order to average colors')

    # Get the mean
    sums[-1] = alpha = math.nan if not totals[-1] else (sums[-1] / totals[-1])
    if math.isnan(alpha):
        alpha = 1.0
    for i in range(chan_count - 1):
        total = totals[i]
        if not total or not alpha:
            sums[i] = math.nan
        elif i == hue_index:
            if premultiplied:
                sin /= total * alpha
                cos /= total * alpha
            else:
                sin /= total
                cos /= total
            if abs(sin) < ACHROMATIC_THRESHOLD and abs(cos) < ACHROMATIC_THRESHOLD:
                sums[i] = math.nan
            else:
                avg_theta = math.degrees(math.atan2(sin, cos))
                sums[i] = (avg_theta + 360) if avg_theta < 0 else avg_theta
        else:
            sums[i] /= (total * alpha) if premultiplied else total

    # Create the color and if polar and there is no defined hue, force an achromatic state.
    color = obj.update(space, sums[:-1], sums[-1])
    if cs.is_polar():
        if is_hwb and math.isnan(color[hue_index]):
            w, b = cs.indexes()[1:]  # type: ignore[attr-defined]
            if color[w] + color[b] < 1:
                color[w] = 1 - color[b]
        elif math.isnan(color[hue_index]) and not math.isnan(color[cs.radial_index()]):  # type: ignore[attr-defined]
            color[cs.radial_index()] = 0  # type: ignore[attr-defined]
    return color
