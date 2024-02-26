"""String serialization."""
from __future__ import annotations
import re
import math
from .. import util
from .. import algebra as alg
from .color_names import to_name
from ..channels import FLG_ANGLE
from ..types import Vector
from typing import TYPE_CHECKING, Sequence, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

RE_COMPRESS = re.compile(r'(?i)^#([a-f0-9])\1([a-f0-9])\2([a-f0-9])\3(?:([a-f0-9])\4)?$')

COMMA = ', '
SLASH = ' / '
SPACE = ' '
EMPTY = ''


def named_color(
    obj: 'Color',
    alpha: bool | None,
    fit: str | bool | dict[str, Any]
) -> str | None:
    """Get the CSS color name."""

    a = get_alpha(obj, alpha, False, False)
    if a is None:
        a = 1
    return to_name(get_coords(obj, fit, False, False) + [a])


def color_function(
    obj: 'Color',
    func: str | None,
    alpha: bool | None,
    precision: int,
    fit: str | bool | dict[str, Any],
    none: bool,
    percent: bool | Sequence[bool],
    legacy: bool,
    scale: float
) -> str:
    """Translate to CSS function form `name(...)`."""

    # Prepare coordinates to be serialized
    a = get_alpha(obj, alpha, none, legacy)
    coords = get_coords(obj, fit, none, legacy)
    if a is not None:
        coords.append(a)

    # `color` should include the color space serialized name.
    if func is None:
        string = ['color({} '.format(obj._space._serialize()[0])]
    # Create the function `name` or `namea` if old legacy form.
    else:
        string = ['{}{}('.format(func, 'a' if legacy and a is not None else EMPTY)]

    # Get channel object and calculate length and the alpha index (last)
    channels = obj._space.channels
    l = len(channels)
    last = l - 1

    # Ensure percent is configured
    # - `True` assumes all but alpha are attempted to be formatted as percents.
    # - A list of booleans will attempt formatting the associated channel as percent,
    #   anything not specified is assumed `False`.
    if isinstance(percent, bool):
        plist = obj._space._percents if percent else []
    else:
        diff = l - len(percent)
        plist = list(percent) + ([False] * diff) if diff > 0 else list(percent)

    # Iterate the coordinates formatting them by scaling the values, formatting for percent, etc.
    for idx, value in enumerate(coords):
        is_last = idx == last
        if is_last:
            string.append(COMMA if legacy else SLASH)
        elif idx != 0:
            string.append(COMMA if legacy else SPACE)
        channel = channels[idx]

        if not (channel.flags & FLG_ANGLE) and plist and plist[idx]:
            span, offset = channel.span, channel.offset
        else:
            span = offset = 0.0
            if not channel.flags & FLG_ANGLE and not is_last:
                value *= scale

        string.append(
            util.fmt_float(
                value,
                precision,
                span,
                offset
            )
        )

    string.append(')')
    return EMPTY.join(string)


def get_coords(
    obj: 'Color',
    fit: bool | str | dict[str, Any],
    none: bool,
    legacy: bool
) -> Vector:
    """Get the coordinates."""

    if fit:
        if fit is True:
            color = obj.fit()
        elif isinstance(fit, str):
            color = obj.fit(method=fit)
        else:
            color = obj.fit(**fit)
    else:
        color = obj
    return color.coords(nans=False if legacy or not none else True)


def get_alpha(
    obj: 'Color',
    alpha: bool | None,
    none: bool,
    legacy: bool
) -> float | None:
    """Get the alpha if required."""

    a = obj.alpha(nans=False if not none or legacy else True)
    alpha = alpha is not False and (alpha is True or a < 1.0 or math.isnan(a))
    return None if not alpha else a


def hexadecimal(
    obj: 'Color',
    alpha: bool | None = None,
    fit: str | bool | dict[str, Any] = True,
    upper: bool = False,
    compress: bool = False
) -> str:
    """Get the hex `RGB` value."""

    coords = get_coords(obj, fit, False, False)
    a = get_alpha(obj, alpha, False, False)

    if a is not None:
        value = "#{:02x}{:02x}{:02x}{:02x}".format(
            int(alg.round_half_up(coords[0] * 255.0)),
            int(alg.round_half_up(coords[1] * 255.0)),
            int(alg.round_half_up(coords[2] * 255.0)),
            int(alg.round_half_up(a * 255.0))
        )
    else:
        value = "#{:02x}{:02x}{:02x}".format(
            int(alg.round_half_up(coords[0] * 255.0)),
            int(alg.round_half_up(coords[1] * 255.0)),
            int(alg.round_half_up(coords[2] * 255.0))
        )

    if upper:
        value = value.upper()

    if compress:
        m = RE_COMPRESS.match(value)
        return (m.expand(r"#\1\2\3\4") if len(value) == 9 else m.expand(r"#\1\2\3")) if m is not None else value
    else:
        return value


def serialize_css(
    obj: 'Color',
    func: str = '',
    color: bool = False,
    alpha: bool | None = None,
    precision: int | None = None,
    fit: bool | str | dict[str, Any] = True,
    none: bool = False,
    percent: bool | Sequence[bool] = False,
    hexa: bool = False,
    upper: bool = False,
    compress: bool = False,
    name: bool = False,
    legacy: bool = False,
    scale: float = 1.0
) -> str:
    """Convert color to CSS."""

    if precision is None:
        precision = obj.PRECISION

    # Color format
    if color:
        return color_function(obj, None, alpha, precision, fit, none, percent, False, 1.0)

    # CSS color names
    if name:
        n = named_color(obj, alpha, fit)
        if n is not None:
            return n

    # Hex RGB
    if hexa:
        return hexadecimal(obj, alpha, fit, upper, compress)

    # Normal CSS named function format
    if func:
        return color_function(obj, func, alpha, precision, fit, none, percent, legacy, scale)

    raise RuntimeError('Could not identify a CSS format to serialize to')  # pragma: no cover
