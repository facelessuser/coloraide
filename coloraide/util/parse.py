"""Parse utilities."""
import re
import math
from .. import util

RGB_CHANNEL_SCALE = 1.0 / 255.0
HUE_SCALE = 1.0 / 360.0
SCALE_PERCENT = 1 / 100.0

CONVERT_TURN = 360
CONVERT_GRAD = 90 / 100

RE_BRACKETS = re.compile(r'(?:(\()|(\))|[^()]+)')
RE_CHAN_SPLIT = re.compile(r'(?:\s*[,/]\s*|\s+)')
RE_COMMA_SPlIT = re.compile(r'(?:\s*,\s*)')

COLOR_PARTS = {
    "percent": r"[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)%",
    "float": r"[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)",
    "angle": r"[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)(deg|rad|turn|grad)?",
    "space": r"\s+",
    "comma": r"\s*,\s*",
    "slash": r"\s*/\s*",
    "sep": r"(?:\s*,\s*|\s+)",
    "asep": r"(?:\s*[,/]\s*|\s+)",
    "hex": r"[a-f0-9]"
}


def norm_percent_channel(value):
    """Normalize percent channel."""

    return float(value.strip('%')) * SCALE_PERCENT


def norm_rgb_channel(value):
    """Normalize RGB channel."""

    if value.endswith("%"):
        return norm_percent_channel(value)
    else:
        return float(value) * RGB_CHANNEL_SCALE


def norm_alpha_channel(value):
    """Normalize alpha channel."""

    if value.endswith("%"):
        value = norm_percent_channel(value)
    else:
        value = float(value)
    return util.clamp(value, 0.0, 1.0)


def norm_lab_lightness(value):
    """Normalize lab channel."""

    return float(value.strip('%'))


def norm_hex_channel(value):
    """Normalize hex channel."""

    return int(value, 16) * RGB_CHANNEL_SCALE


def norm_angle(angle):
    """Normalize angle units."""

    if angle.endswith('turn'):
        value = float(angle[:-4]) * CONVERT_TURN
    elif angle.endswith('grad'):
        value = float(angle[:-4]) * CONVERT_GRAD
    elif angle.endswith('rad'):
        value = math.degrees(float(angle[:-3]))
    elif angle.endswith('grad'):
        value = float(angle[:-3]) * CONVERT_GRAD
    elif angle.endswith('deg'):
        value = float(angle[:-3])
    else:
        value = float(angle)
    return value


def norm_hue_channel(value):
    """Normalize hex channel."""

    angle = norm_angle(value)
    return norm_deg_channel(angle)


def norm_deg_channel(value, scale=360.0):
    """Normalize degree channel."""

    value = float(value)
    value /= scale

    if not (0.0 <= value <= 1.0):
        value = value % 1.0
    return value


def bracket_match(match, string, start, fullmatch):
    """
    Make sure we can acquire a complete `func()` before we replace variables.

    We mainly do this so we can judge the real size before we alter the string with variables.
    """

    end = None
    if match.match(string, start):
        brackets = 1
        for m in RE_BRACKETS.finditer(string, start + 6):
            if m.group(2):
                brackets -= 1
            elif m.group(1):
                brackets += 1

            if brackets == 0:
                end = m.end(2)
                break
    return end if (not fullmatch or end == len(string)) else None
