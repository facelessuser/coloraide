"""Colors."""
import re
import functools
from .srgb import _SRGB
from .hsl import _HSL
from .hwb import _HWB
from .lab import _LAB
from .lch import _LCH

__all__ = ("SRGB", "HSL", "HWB", "LAB", "LCH")

RE_VARS = re.compile(r'(?i)\b(var\(\s*([-\w][-\w\d]*)\s*\))')


class _ColorConvert:
    """A mix-in to allow converting between the various classes."""

    def convert(self, space):
        """Convert to color space."""

        obj = CS_MAP.get(space.lower())
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        return obj(self)

    def new(self, space, value):
        """Create new color in color space."""

        obj = CS_MAP.get(space.lower())
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        return obj(value)


class SRGB(_ColorConvert, _SRGB):
    """RGB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class HSL(_ColorConvert, _HSL):
    """HSL color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class HWB(_ColorConvert, _HWB):
    """HWB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class LAB(_ColorConvert, _LAB):
    """HWB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class LCH(_ColorConvert, _LCH):
    """HWB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


SUPPORTED = [HSL, HWB, LAB, LCH, SRGB]

CS_MAP = {}
for obj in SUPPORTED:
    CS_MAP[obj.get_colorspace()] = obj


def _var_replace(m, var=None):
    """Replace variables."""

    replacement = var.get(m.group(2))
    return replacement if replacement is not None else ""


def handle_vars(string, variables):
    """Handle CSS variables."""

    n = 1
    while n:
        string, n = RE_VARS.subn(functools.partial(_var_replace, var=variables), string)
    return string


def colorcss(string, variables=None):
    """Parse a CSS color."""

    if variables:
        string = handle_vars(string, variables)

    for colorspace in SUPPORTED:
        value = colorspace.css_match(string)
        if value is not None:
            obj = colorspace(value)
            return obj
    raise ValueError("'{}' doesn't appear to be a valid and/or supported CSS color".format(string))
