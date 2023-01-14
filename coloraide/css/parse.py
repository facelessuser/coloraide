"""Parse utilities."""
from __future__ import annotations
import re
import math
from .. import algebra as alg
from ..types import Vector
from . import color_names
from ..channels import Channel, FLG_ANGLE
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..spaces import Space

RGB_CHANNEL_SCALE = 1.0 / 255.0
HUE_SCALE = 1.0 / 360.0
SCALE_PERCENT = 1 / 100.0

CONVERT_TURN = 360
CONVERT_GRAD = 90 / 100

RE_CHAN_SPLIT = re.compile(r'(?:\s*[,/]\s*|\s+)')
RE_COMMA_SPlIT = re.compile(r'(?:\s*,\s*)')
RE_SLASH_SPLIT = re.compile(r'(?:\s*/\s*)')

COLOR_PARTS = {
    "strict_percent": r"(?:[+\-]?(?:[0-9]*\.)?[0-9]+(?:e[-+]?[0-9]*)?%)",
    "strict_float": r"(?:[+\-]?(?:[0-9]*\.)?[0-9]+(?:e[-+]?[0-9]*)?)",
    "strict_angle": r"(?:[+\-]?(?:[0-9]*\.)?[0-9]+(?:e[-+]?[0-9]*)?(?:deg|rad|turn|grad)?)",
    "percent": r"(?:[+\-]?(?:[0-9]*\.)?[0-9]+(?:e[-+]?[0-9]*)?%|none)",
    "float": r"(?:[+\-]?(?:[0-9]*\.)?[0-9]+(?:e[-+]?[0-9]*)?|none)",
    "angle": r"(?:[+\-]?(?:[0-9]*\.)?[0-9]+(?:e[-+]?[0-9]*)?(?:deg|rad|turn|grad)?|none)",
    "space": r"\s+",
    "comma": r"\s*,\s*",
    "slash": r"\s*/\s*",
    "sep": r"(?:\s*,\s*|\s+)",
    "asep": r"(?:\s*[,/]\s*|\s+)",
    "hex": r"[a-f0-9]"
}

# Allow 15 channels maximum. This should be able to handle any colors we throw at it.
RE_COLOR_MATCH = re.compile(
    r"""(?xi)
    color\(\s*
    (-{{0,2}}[a-z][-a-z0-9_]*)
    ((?:{space}(?:{strict_percent}|{float})){{1,15}}(?:{slash}(?:{strict_percent}|{float}))?)
    \s*\)
    """.format(
        **COLOR_PARTS
    )
)

CSS_MATCH = {
    'srgb': re.compile(
        r"""(?xi)
        (?:
            # RGB syntax
            \b(rgba?)\(\s*
            (?:
                # Space separated format
                (?:
                    # Float form
                    (?:{float}{space}){{2}}{float} |
                    # Percent form
                    (?:{percent}{space}){{2}}{percent}
                )({slash}(?:{strict_percent}|{float}))? |
                # Comma separated format
                (?:
                    # Float form
                    (?:{strict_float}{comma}){{2}}{strict_float} |
                    # Percent form
                    (?:{strict_percent}{comma}){{2}}{strict_percent}
                )({comma}(?:{strict_percent}|{strict_float}))?
            )
            \s*\) |
            # Hex syntax
            \#(?:{hex}{{6}}(?:{hex}{{2}})?|{hex}{{3}}(?:{hex})?)\b |
            # Names
            \b[a-z]{{3,}}\b
        )
        """.format(**COLOR_PARTS)
    ),
    'hsl': re.compile(
        r"""(?xi)
        \b(hsla?)\(\s*
        (?:
            # Space separated format
            {angle}{space}{percent}{space}{percent}(?:{slash}(?:{strict_percent}|{float}))? |
            # comma separated format
            {strict_angle}{comma}{strict_percent}{comma}{strict_percent}(?:{comma}(?:{strict_percent}|{strict_float}))?
        )
        \s*\)
        """.format(**COLOR_PARTS)
    ),
    'hwb': re.compile(
        r"""(?xi)
        \b(hwb)\(\s*
        (?:
            # Space separated format
            {angle}(?:{space}{percent}){{2}}(?:{slash}(?:{strict_percent}|{float}))?
        )
        \s*\)
        """.format(**COLOR_PARTS)
    ),
    'lab': re.compile(
        r"""(?xi)
        (?:
            \b(lab)\(\s*
            (?:
                # Space separated format
                (?:{strict_percent}|{float})(?:{space}(?:{strict_percent}|{float})){{2}}
                (?:{slash}(?:{strict_percent}|{float}))?
            )
            \s*\)
        )
        """.format(**COLOR_PARTS)
    ),
    'lch': re.compile(
        r"""(?xi)
        \b(lch)\(\s*
        (?:
            # Space separated format
            (?:(?:{strict_percent}|{float}){space}){{2}}{angle}(?:{slash}(?:{strict_percent}|{float}))?
        )
        \s*\)
        """.format(**COLOR_PARTS)
    ),
    'oklab': re.compile(
        r"""(?xi)
        (?:
            \b(oklab)\(\s*
            (?:
                # Space separated format
                (?:{strict_percent}|{float})(?:{space}(?:{strict_percent}|{float})){{2}}
                (?:{slash}(?:{strict_percent}|{float}))?
            )
            \s*\)
        )
        """.format(**COLOR_PARTS)
    ),
    'oklch': re.compile(
        r"""(?xi)
        \b(oklch)\(\s*
        (?:
            # Space separated format
            (?:(?:{strict_percent}|{float}){space}){{2}}{angle}(?:{slash}(?:{strict_percent}|{float}))?
        )
        \s*\)
        """.format(**COLOR_PARTS)
    )
}


def norm_float(string: str) -> float:
    """Normalize a float value."""

    if string == "none":
        return alg.NaN
    elif string.lower().endswith(('e-', 'e+', 'e')):
        string += '0'
    return float(string)


def norm_hex_channel(string: str) -> float:
    """Normalize the hex string to a form we can handle."""

    return int(string, 16) * RGB_CHANNEL_SCALE


def norm_percent_channel(string: str, scale: float = 100, offset: float = 0.0) -> float:
    """Normalize percent channel."""

    if string == 'none':  # pragma: no cover
        return norm_float(string)
    elif string.endswith('%'):
        value = norm_float(string[:-1])
        return (value * scale * 0.01) - offset if scale != 100 else value
    else:  # pragma: no cover
        # Should only occur internally if we are doing something wrong.
        raise ValueError("Unexpected value '{}'".format(string))


def norm_color_channel(string: str, scale: float = 1, offset: float = 0.0) -> float:
    """Normalize percent channel."""

    if string.endswith('%'):
        return norm_percent_channel(string, scale, offset)
    else:
        return norm_float(string)


def norm_rgb_channel(string: str, scale: float = 1) -> float:
    """Normalize RGB channel."""

    if string.endswith("%"):
        return norm_percent_channel(string, scale)
    else:
        return norm_float(string) * RGB_CHANNEL_SCALE


def norm_alpha_channel(string: str) -> float:
    """Normalize alpha channel."""

    if string.endswith("%"):
        value = norm_percent_channel(string, 1)
    else:
        value = norm_float(string)
    return alg.clamp(value, 0.0, 1.0)


def norm_angle_channel(angle: str) -> float:
    """Normalize angle units."""

    if angle.endswith('turn'):
        value = norm_float(angle[:-4]) * CONVERT_TURN
    elif angle.endswith('grad'):
        value = norm_float(angle[:-4]) * CONVERT_GRAD
    elif angle.endswith('rad'):
        value = math.degrees(norm_float(angle[:-3]))
    elif angle.endswith('deg'):
        value = norm_float(angle[:-3])
    else:
        value = norm_float(angle)
    return value


def parse_hex(color: str) -> tuple[Vector, float]:
    """Parse hexadecimal color."""
    length = len(color)
    if length in (7, 9):
        return (
            [
                norm_hex_channel(color[1:3]),
                norm_hex_channel(color[3:5]),
                norm_hex_channel(color[5:7])
            ],
            norm_hex_channel(color[7:9]) if length == 9 else 1.0
        )
    else:
        return (
            [
                norm_hex_channel(color[1] * 2),
                norm_hex_channel(color[2] * 2),
                norm_hex_channel(color[3] * 2)
            ],
            norm_hex_channel(color[4] * 2) if length == 5 else 1.0
        )


def parse_rgb_channels(color: str, boundry: tuple[Channel, ...]) -> tuple[Vector, float]:
    """Parse CSS RGB format."""
    channels = []
    alpha = 1.0
    for i, c in enumerate(RE_CHAN_SPLIT.split(color.strip()), 0):
        c = c.lower()
        if i <= 2:
            channels.append(norm_rgb_channel(c, boundry[i].high))
        elif i == 3:
            alpha = norm_alpha_channel(c)
    return channels, alpha


def parse_channels(color: str, boundry: tuple[Channel, ...]) -> tuple[Vector, float]:
    """Parse CSS RGB format."""

    channels = []
    alpha = 1.0
    length = len(boundry)
    for i, c in enumerate(RE_CHAN_SPLIT.split(color.strip()), 0):
        c = c.lower()
        if i < length:
            bound = boundry[i]
            if bound.flags & FLG_ANGLE:
                channels.append(norm_angle_channel(c))
            else:
                channels.append(norm_color_channel(c, bound.high))
        elif i == length:
            alpha = norm_alpha_channel(c)
    return channels, alpha


def parse_color(
    string: str,
    spaces: dict[str, Space],
    start: int,
    fullmatch: bool = False
) -> Optional[tuple[Space, tuple[Vector, float], int]]:
    """Perform default color matching."""

    m = RE_COLOR_MATCH.match(string, start)
    if m is not None and (not fullmatch or m.end(0) == len(string)):
        ident = m.group(1).lower()

        # Iterate the spaces and see if we find the color serialization identifier
        for space in spaces.values():
            if ident in space._serialize():
                # Break channels up into a list
                num_channels = len(space.CHANNELS)
                split = RE_SLASH_SPLIT.split(m.group(2).strip(), maxsplit=1)

                # Get alpha channel
                alpha = norm_alpha_channel(split[-1].lower()) if len(split) > 1 else 1.0

                # Parse color channels
                channels = []
                i = -1
                properties = space.CHANNELS
                for i, c in enumerate(RE_CHAN_SPLIT.split(split[0]), 0):
                    if c and i < num_channels:
                        channel = properties[i]
                        channels.append(norm_color_channel(c.lower(), channel.span, channel.offset))
                    else:
                        # Not the right amount of channels
                        break

                # Apply null adjustments (null hues) if applicable
                # or return None if we got the wrong amount of channels
                if i + 1 == num_channels:
                    return space, (channels, alpha), m.end(0)
                break
    return None


def parse_css(
    cspace: Space,
    string: str,
    start: int = 0,
    fullmatch: bool = True,
    color: bool = False
) -> Optional[tuple[tuple[Vector, float], int]]:
    """Match a CSS color string."""

    name = cspace.NAME
    if name == 'srgb':
        m = CSS_MATCH[cspace.NAME].match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            string = string[m.start(0):m.end(0)].lower()
            if string.startswith('#'):
                return parse_hex(string), m.end(0)
            elif not string.startswith('rgb'):
                value = color_names.from_name(string)
                if value is not None:
                    return (value[:3], value[3]), m.end(0)
            else:
                offset = m.start(0)
                return (
                    parse_rgb_channels(string[m.end(1) - offset + 1:m.end(0) - offset - 1], cspace.CHANNELS),
                    m.end(0)
                )
    else:
        m = CSS_MATCH[cspace.NAME].match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            return parse_channels(string[m.end(1) + 1:m.end(0) - 1], cspace.CHANNELS), m.end(0)

    # If we wanted to support per color matching of this format, we could enable this.
    # It is much faster to generically match all `color(space ...)` instances and then
    # just see if the `spaces` matches any of the registered spaces that have opted in.
    # Repeatedly performing this step over and over for each space just isn't efficient.
    if color:  # pragma: no cover
        result = parse_color(string, {cspace.NAME: cspace}, start, fullmatch)
        if result is not None:
            return result[1:]

    return None  # pragma: no cover
