"""Matcher."""

EMPTY = tuple()
EMPTY_SET = frozenset()


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


def color_fullmatch(string, supported=EMPTY, spaces=EMPTY_SET):
    """Match a color and return the object."""

    if spaces is None:
        spaces = []

    m = color_match(string, fullmatch=True, supported=supported, spaces=spaces)
    if m is not None:
        return m.color


def color_match(string, start=0, fullmatch=False, supported=EMPTY, spaces=EMPTY_SET):
    """Match a color at the given position."""

    for space in supported:
        if space.SPACE not in spaces:
            continue
        value, match_end = space.match(string, start, fullmatch)
        if value is not None:
            obj = space(value)
            return ColorMatch(obj, start, match_end)
    return None
