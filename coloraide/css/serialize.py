"""String serialization."""
from __future__ import annotations
import re
import math
from .. import util
from .. import algebra as alg
from .color_names import to_name
from ..channels import FLG_PERCENT, FLG_OPT_PERCENT, FLG_ANGLE
from ..types import Vector
from typing import TYPE_CHECKING

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
    fit: str | bool
) -> str | None:
    """Get the CSS color name."""

    a = get_alpha(obj, alpha, False, False)
    if a is None:
        a = 1
    return to_name(get_coords(obj, fit, False, False) + [a])


def named_color_function(
    obj: 'Color',
    func: str,
    alpha: bool | None,
    precision: int,
    fit: str | bool,
    none: bool,
    percent: bool,
    legacy: bool,
    scale: float
) -> str:
    """Translate to CSS function form `name(...)`."""

    # Create the function `name` or `namea` if old legacy form.
    a = get_alpha(obj, alpha, none, legacy)
    string = ['{}{}('.format(func, 'a' if legacy and a is not None else EMPTY)]

    # Iterate the coordinates formatting them for percent, not percent, and even scaling them (sRGB).
    coords = get_coords(obj, fit, none, legacy)
    channels = obj._space.CHANNELS
    for idx, value in enumerate(coords):
        channel = channels[idx]
        use_percent = channel.flags & FLG_PERCENT or (percent and channel.flags & FLG_OPT_PERCENT)
        is_angle = channel.flags & FLG_ANGLE
        if not use_percent and not is_angle:
            value *= scale
        if idx != 0:
            string.append(COMMA if legacy else SPACE)
        string.append(
            util.fmt_float(
                value,
                precision,
                channel.span if use_percent else 0.0,
                channel.offset if use_percent else 0.0
            )
        )

    # Add alpha if needed
    if a is not None:
        string.append('{}{})'.format(COMMA if legacy else SLASH, util.fmt_float(a, max(precision, util.DEF_PREC))))
    else:
        string.append(')')
    return EMPTY.join(string)


def color_function(
    obj: 'Color',
    alpha: bool | None,
    precision: int,
    fit: str | bool,
    none: bool
) -> str:
    """Color format."""

    # Export in the `color(space ...)` format
    coords = get_coords(obj, fit, none, False)
    a = get_alpha(obj, alpha, none, False)
    return (
        'color({} {}{})'.format(
            obj._space._serialize()[0],
            SPACE.join([util.fmt_float(coord, precision) for coord in coords]),
            SLASH + util.fmt_float(a, max(precision, util.DEF_PREC)) if a is not None else EMPTY
        )
    )


def get_coords(
    obj: 'Color',
    fit: str | bool,
    none: bool,
    legacy: bool
) -> Vector:
    """Get the coordinates."""

    color = (obj.fit(method=None if not isinstance(fit, str) else fit) if fit else obj)
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
    fit: str | bool = True,
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
    fit: str | bool = True,
    none: bool = False,
    percent: bool = False,
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
        return color_function(obj, alpha, precision, fit, none)

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
        return named_color_function(obj, func, alpha, precision, fit, none, percent, legacy, scale)

    raise RuntimeError('Could not identify a CSS format to serialize to')  # pragma: no cover
