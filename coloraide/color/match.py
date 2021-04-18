"""Match input colors."""


class ColorMatch:
    """Color match object."""

    def __init__(self, color, start, end):
        """Initialize."""

        self.color = color
        self.start = start
        self.end = end

    def __str__(self):  # pragma: no cover
        """String."""

        return "ColorMatch(color={!r}, start={}, end={})".format(self.color, self.start, self.end)

    __repr__ = __str__


class Match:
    """Match support."""

    @classmethod
    def _match(cls, string, start=0, fullmatch=False, filters=None):
        """
        Match a color in a buffer and return a color object.

        This must return the color space, not the Color object.
        """

        filters = set(filters) if filters is not None else set()

        for space, space_class in cls.CS_MAP.items():
            if filters and space not in filters:
                continue
            value, match_end = space_class.match(string, start, fullmatch)
            if value is not None:
                color = space_class(*value)
                return ColorMatch(color, start, match_end)
        return None

    @classmethod
    def match(cls, string, start=0, fullmatch=False, *, filters=None):
        """Match color."""

        obj = cls._match(string, start, fullmatch, filters=filters)
        if obj is not None:
            obj.color = cls(obj.color.space(), obj.color.coords(), obj.color.alpha)
        return obj
