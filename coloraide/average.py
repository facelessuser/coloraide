"""Average colors together."""
from __future__ import annotations
import math
from .types import ColorInput, Vector
from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color


def premultiply(color: Color, hue_index: int, alphas: Vector, enabled: bool) -> Vector:
    """Premultiply the color before averaging."""

    alpha = color.alpha()
    alphas.append(alpha)

    if not enabled or math.isnan(alpha) or alpha == 1.0:
        return color.coords()

    return [c if e == hue_index else c * alpha for e, c in enumerate(color.coords())]


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


def average(create: type[Color], colors: Sequence[ColorInput], space: str, premultiplied: bool = True) -> Color:
    """Average a list of colors together."""

    obj = create(space, [])

    # Check if there are enough colors to average.
    length = len(colors)
    if not length:
        raise ValueError('At least one color must be provided in order to average colors')
    elif length == 1:
        return obj.new(colors[0]).convert(space, in_place=True)

    # Get channel information
    cs = obj.CS_MAP[space]
    hue_index = cs.hue_index() if hasattr(cs, 'hue_index') else -1
    channels = cs.channels
    coords = [] * len(channels)

    # Convert to desired space and premultiply values. Wrap in zip to iterate values per channel.
    # Alpha will be collected in a separate list.
    alphas = []  # type: Vector
    zipped = zip(
        *[premultiply(obj.new(c).convert(space, in_place=True), hue_index, alphas, premultiplied) for c in colors]
    )

    # Average each color channel
    for e, points in enumerate(zipped):
        div = s = c = value = 0.0
        for e2, p in enumerate(points):
            alpha = alphas[e2]
            # Undefined values do not contribute
            if not math.isnan(p):
                if e == hue_index:
                    # Hue doesn't care about alpha
                    div += 1
                    rad = math.radians(p)
                    s += math.sin(rad)
                    c += math.cos(rad)
                else:
                    # Non-hues are weighted averages based on transparency
                    div += 1
                    value += p

        # Divide by the weighted average.
        if e == hue_index:
            coords.append(math.degrees(math.atan2(s / div, c / div)))
        else:
            coords.append(value / div if div else value)

    # Average alpha
    alpha = count = 0.0
    for a in alphas:
        if math.isnan(a):
            continue
        count += 1
        alpha += a
    coords.append(alpha / count if count else alpha)

    # Undo premultiplication
    if premultiplied:
        coords = postdivide(coords, hue_index)

    # Return the color
    return obj.update(space, coords[:-1], coords[-1])
