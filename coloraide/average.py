"""Average colors together."""
from __future__ import annotations
import math
from . import util
import itertools as it
from .spaces import HWBish
from .types import ColorInput, AnyColor
from typing import Iterable


class Sentinel(float):
    """Sentinel object that is specific to averaging that we shouldn't see defined anywhere else."""


def _iter_colors(colors: Iterable[ColorInput]) -> Iterable[tuple[ColorInput, float]]:
    """Iterate colors and return weights."""

    for c in colors:
        yield c, 1.0


def average(
    color_cls: type[AnyColor],
    colors: Iterable[ColorInput],
    weights: Iterable[float] | None,
    space: str,
    premultiplied: bool = True
) -> AnyColor:
    """
    Average a list of colors together.

    Polar coordinates use a circular mean: https://en.wikipedia.org/wiki/Circular_mean.
    """

    sentinel = Sentinel()
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
    no_weights = weights is None
    if no_weights:
        weights = ()
    mx = 0.0

    # Sum channel values using a rolling average. Apply premultiplication and additional weighting as required.
    count = 0
    for c, w in (_iter_colors(colors) if no_weights else it.zip_longest(colors, weights, fillvalue=sentinel)):  # type: ignore[arg-type]

        # Handle explicit weighted cases
        if not no_weights:
            # If there are more weights than colors, ignore additional weights
            if c is sentinel:
                break

            # If there are less weights than colors, assume full weight for colors without weights
            if w is sentinel:
                w = mx

            # Negative weights are considered as zero weight
            if w < 0.0:
                w = 0.0

            # Track the largest weight so we can populate colors with no weights
            elif w > mx:
                mx = w

        obj.update(c)  # type: ignore[arg-type]
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

    # Undo premultiplication and weighting to get the final color.
    # Adjust a channel to be undefined if all values in channel were undefined or if it is an achromatic hue channel.
    if not wavg:
        wavg = math.nan
    avgs[-1] = alpha = math.nan if not counts[-1] else avgs[-1] / wavg
    if math.isnan(alpha):
        alpha = 1.0
    factor = (alpha * wavg) if premultiplied else wavg

    for i in range(chan_count - 1):
        if not counts[i] or not alpha:
            avgs[i] = math.nan
        elif i == hue_index:
            sin /= factor
            cos /= factor
            # Combine polar parts into a degree
            if abs(sin) < util.ACHROMATIC_THRESHOLD_SM and abs(cos) < util.ACHROMATIC_THRESHOLD_SM:
                avgs[i] = math.nan
            else:
                avg_theta = math.degrees(math.atan2(sin, cos))
                avgs[i] = (avg_theta + 360) if avg_theta < 0 else avg_theta
        else:
            avgs[i] /= factor

    # Create the color. If polar and there is no defined hue, force an achromatic state.
    color = obj.update(space, avgs[:-1], avgs[-1])
    if cs.is_polar():
        if is_hwb and math.isnan(color[hue_index]):
            w, b = cs.indexes()[1:]  # type: ignore[attr-defined]
            if color[w] + color[b] < 1:
                color[w] = 1 - color[b]
        elif math.isnan(color[hue_index]) and not math.isnan(color[cs.radial_index()]):  # type: ignore[attr-defined]
            color[cs.radial_index()] = 0  # type: ignore[attr-defined]
    return color
