"""Parse utilities."""
import re
import math
from . import util

RGB_CHANNEL_SCALE = 1.0 / 255.0
HUE_SCALE = 1.0 / 360.0
SCALE_PERCENT = 1 / 100.0

CONVERT_TURN = 360
CONVERT_GRAD = 90 / 100

RE_CHAN_SPLIT = re.compile(r'(?:\s*[,/]\s*|\s+)')
RE_COMMA_SPlIT = re.compile(r'(?:\s*,\s*)')
RE_SLASH_SPLIT = re.compile(r'(?:\s*/\s*)')

COLOR_PARTS = {
    "strict_percent": r"(?:[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)(?:e[-+]?[0-9]*)?%)",
    "strict_float": r"(?:[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)(?:e[-+]?[0-9]*)?)",
    "strict_angle": r"(?:[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)(?:e[-+]?[0-9]*)?(?:deg|rad|turn|grad)?)",
    "percent": r"(?:[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)(?:e[-+]?[0-9]*)?%|none)",
    "float": r"(?:[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)(?:e[-+]?[0-9]*)?|none)",
    "angle": r"(?:[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)(?:e[-+]?[0-9]*)?(?:deg|rad|turn|grad)?|none)",
    "space": r"\s+",
    "comma": r"\s*,\s*",
    "slash": r"\s*/\s*",
    "sep": r"(?:\s*,\s*|\s+)",
    "asep": r"(?:\s*[,/]\s*|\s+)",
    "hex": r"[a-f0-9]"
}


def norm_float(string: str) -> float:
    """Normalize a float value."""

    if string == "none":
        return util.NaN
    elif string.lower().endswith(('e-', 'e+', 'e')):
        string += '0'
    return float(string)


def norm_hex_channel(string: str) -> float:
    """Normalize the hex string to a form we can handle."""

    if string.startswith('#'):
        return int(string[1:], 16) * RGB_CHANNEL_SCALE
    else:  # pragma: no cover
        # Should only occur internally if we are doing something wrong.
        raise ValueError("Unexpected value '{}'".format(string))


def norm_percent_channel(string: str, scale: float = 100) -> float:
    """Normalize percent channel."""

    if string == 'none':
        return norm_float(string)
    elif string.endswith('%'):
        value = norm_float(string[:-1])
        return value * scale * 0.01 if scale != 100 else value
    else:  # pragma: no cover
        # Should only occur internally if we are doing something wrong.
        raise ValueError("Unexpected value '{}'".format(string))


def norm_color_channel(string: str, scale: float = 1) -> float:
    """Normalize percent channel."""

    if string.endswith('%'):
        return norm_percent_channel(string, scale)
    else:
        return norm_float(string)


def norm_rgb_channel(string: str) -> float:
    """Normalize RGB channel."""

    if string.endswith("%"):
        return norm_percent_channel(string, True)
    else:
        return norm_float(string) * RGB_CHANNEL_SCALE


def norm_alpha_channel(string: str) -> float:
    """Normalize alpha channel."""

    if string.endswith("%"):
        value = norm_percent_channel(string, True)
    else:
        value = norm_float(string)
    return util.clamp(value, 0.0, 1.0)


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
