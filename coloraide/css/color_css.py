"""CSS matching."""
from ..util import parse
from .colors import SUPPORTED


class ColorMatch:
    """Color match object."""

    def __init__(self, color, start, end):
        """Initialize."""

        self.color = color
        self.start = start
        self.end = end

    def __str__(self):
        """String."""

        return "ColorMatch(color={!r}, start={}, end={})".format(self.color, self.start, self.end)

    __repr__ = __str__


def colorcss(string, variables=None):
    """Parse a CSS color."""

    match = colorcss_match(string, variables, fullmatch=True)
    if match is not None:
        return match.color


def colorcss_match(string, variables=None, start=0, fullmatch=False):
    """Match a color at the given position."""

    end = None
    if variables:
        m = parse.RE_VARS.match(string, start)
        if m and (not fullmatch or len(string) == m.end(0)):
            end = m.end(0)
            start = 0
            string = string[start:end]
            string = parse.handle_vars(string, variables)
            variables = None

    for colorspace in SUPPORTED:
        value, match_end = colorspace.match(string, start, fullmatch, variables)
        if value is not None:
            obj = colorspace(value)
            return ColorMatch(obj, start, end if end is not None else match_end)
