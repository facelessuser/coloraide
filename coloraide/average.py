"""Average colors together."""
from __future__ import annotations
import math
import itertools as it
from . import util
from .spaces import HWBish
from .types import ColorInput, AnyColor
from typing import Iterable


def average(
    color_cls: type[AnyColor],
    colors: Iterable[ColorInput],
    weights: Iterable[float],
    space: str,
    premultiplied: bool = True
) -> AnyColor:
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
    avgs = [0.0] * chan_count
    counts = [0] * chan_count
    sin = 0.0
    cos = 0.0
    wavg = 0.0

    # Sum channel values
    count = 0
    for c, w in it.zip_longest(colors, weights):
        if c is None:
            raise ValueError('Not enough colors provided to satisfy number of weights')
        if w is None:
            w = 1.0
        else:
            w = max(0.0, w)
        obj.update(c)
        # If cylindrical color is achromatic, ensure hue is undefined
        if hue_index >= 0 and not math.isnan(obj[hue_index]) and obj.is_achromatic():
            obj[hue_index] = math.nan
        coords = obj[:]
        alpha = coords[-1]
        if math.isnan(alpha):
            alpha = 1.0
        walpha = alpha * w
        count += 1
        wavg += (w - wavg) / count
        i = 0
        for coord in coords:
            # No need to average an undefined value or color components if alpha is zero
            is_alpha = i == alpha_index
            if not math.isnan(coord) and (premultiplied or alpha or is_alpha):
                counts[i] += 1
                n = counts[i]
                if i == hue_index:
                    rad = math.radians(coord)
                    if premultiplied:
                        sin += ((math.sin(rad) * walpha) - sin) / n
                        cos += ((math.cos(rad) * walpha) - cos) / n
                    else:
                        sin += ((math.sin(rad) * w) - sin) / n
                        cos += ((math.cos(rad) * w) - cos) / n
                else:
                    avgs[i] += (((coord * walpha) if premultiplied and not is_alpha else (coord * w)) - avgs[i]) / n
            i += 1

    if not count:
        raise ValueError('At least one color must be provided in order to average colors')

    # Get the mean
    w_factor = math.nan if not wavg else wavg
    avgs[-1] = alpha = math.nan if not counts[-1] else avgs[-1] / w_factor
    if math.isnan(alpha):
        alpha = 1.0
    walpha = alpha * w_factor

    for i in range(chan_count - 1):
        if not counts[i] or not alpha:
            avgs[i] = math.nan
        elif i == hue_index:
            if premultiplied:
                sin /= walpha
                cos /= walpha
            else:
                sin /= w_factor
                cos /= w_factor
            if abs(sin) < util.ACHROMATIC_THRESHOLD_SM and abs(cos) < util.ACHROMATIC_THRESHOLD_SM:
                avgs[i] = math.nan
            else:
                avg_theta = math.degrees(math.atan2(sin, cos))
                avgs[i] = (avg_theta + 360) if avg_theta < 0 else avg_theta
        else:
            avgs[i] /= walpha if premultiplied else w_factor

    # Create the color and if polar and there is no defined hue, force an achromatic state.
    color = obj.update(space, avgs[:-1], avgs[-1])
    if cs.is_polar():
        if is_hwb and math.isnan(color[hue_index]):
            w, b = cs.indexes()[1:]  # type: ignore[attr-defined]
            if color[w] + color[b] < 1:
                color[w] = 1 - color[b]
        elif math.isnan(color[hue_index]) and not math.isnan(color[cs.radial_index()]):  # type: ignore[attr-defined]
            color[cs.radial_index()] = 0  # type: ignore[attr-defined]
    return color
