"""Parse utilities."""
import re
import math
from .. import util

RGB_CHANNEL_SCALE = 1.0 / 255.0
HUE_SCALE = 1.0 / 360.0
SCALE_PERCENT = 1 / 100.0
SCALE_A_B = 1 / 320.0
SHIFT_A_B = 160.0

CONVERT_TURN = 360
CONVERT_GRAD = 90 / 100

RE_VARS = re.compile(r'(?i)(?:(?<=^)|(?<=[\s\t\(,/]))(var\(\s*([-\w][-\w\d]*)\s*\))(?!\()(?=[\s\t\),/]|$)')
RE_BRACKETS = re.compile(r'(?:(\()|(\))|[^()]+)')
RE_CHAN_SPLIT = re.compile(r'(?:\s*[,/]\s*|\s+)')

COLOR_PARTS = {
    "percent": r"[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)%",
    "float": r"[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)",
    "angle": r"[+\-]?(?:(?:[0-9]*\.[0-9]+)|[0-9]+)(deg|rad|turn|grad)?",
    "space": r"\s+",
    "comma": r"\s*,\s*",
    "slash": r"\s*/\s*",
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

    return float(value)


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
    if not (0.0 <= angle <= 360.0):
        angle % 360.0
    return angle * HUE_SCALE


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
