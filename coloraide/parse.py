"""Parse utilities."""
import re
import math
import functools
from . import util

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
    "hex": r"[a-f0-9]"
}

tokens = {
    "units": re.compile(
        r"""(?xi)
        # Some number of units separated by valid separators
        (?:
            {float} |
            {angle} |
            {percent} |
            \#(?:{hex}{{6}}(?:{hex}{{2}})?|{hex}{{3}}(?:{hex})?) |
            [\w][\w\d]*
        )
        """.format(**COLOR_PARTS)
    ),
    "functions": re.compile(r'(?i)[\w][\w\d]*\('),
    "separators": re.compile(r'(?:{comma}|{space}|{slash})'.format(**COLOR_PARTS))
}

RE_VARS = re.compile(r'(?i)(?:(?<=^)|(?<=[\s\t\(,/]))(var\(\s*([-\w][-\w\d]*)\s*\))(?!\()(?=[\s\t\),/]|$)')


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


def validate_vars(var, good_vars):
    """
    Validate variables.

    We will blindly replace values, but if we are fairly confident they follow
    the pattern of a valid, complete unit, if you replace them in a bad place,
    it will break the color (as it should) and if not, it is likely to parse fine,
    unless it breaks the syntax of the color being evaluated.
    """

    for k, v in var.items():
        v = v.strip()
        start = 0
        need_sep = False
        length = len(v)
        while True:
            if start == length:
                good_vars[k] = v
                break
            try:
                # Each item should be separated by some valid separator
                if need_sep:
                    m = tokens["separators"].match(v, start)
                    if m:
                        start = m.end(0)
                        need_sep = False
                        continue
                    else:
                        break

                # Validate things like `rgb()`, `contrast()` etc.
                m = tokens["functions"].match(v, start)
                if m:
                    end = None
                    brackets = 1
                    for m in RE_BRACKETS.finditer(v, start + 6):
                        if m.group(2):
                            brackets -= 1
                        elif m.group(1):
                            brackets += 1

                        if brackets == 0:
                            end = m.end(0)
                            break
                    if end is None:
                        break
                    start = end
                    need_sep = True
                    continue

                # Validate that units such as percents, floats, hex colors, etc.
                m = tokens["units"].match(v, start)
                if m:
                    start = m.end(0)
                    need_sep = True
                    continue
                break
            except Exception:
                break


def _var_replace(m, var=None, parents=None):
    """Replace variables but try to prevent infinite recursion."""

    name = m.group(2)
    replacement = var.get(m.group(2))
    string = replacement if replacement and name not in parents is not None else ""
    parents.add(name)
    return RE_VARS.sub(functools.partial(_var_replace, var=var, parents=parents), string)


def handle_vars(string, variables, parents=None):
    """Handle CSS variables."""

    temp_vars = {}
    validate_vars(variables, temp_vars)
    parent_vars = set() if parents is None else parents

    return RE_VARS.sub(functools.partial(_var_replace, var=temp_vars, parents=parent_vars), string)
