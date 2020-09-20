"""Colors."""
from .hsv import HSV
from .srgb import SRGB
from .hsl import HSL
from .hwb import HWB
from .lab import LAB
from .lch import LCH
from .display_p3 import Display_P3
from .a98_rgb import A98_RGB
from .prophoto_rgb import ProPhoto_RGB
from .rec_2020 import Rec_2020
from .. import util


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


class Color:
    """Color wrapper class."""

    SUPPORTED = (
        HSL, HWB, LAB, LCH, SRGB, HSV,
        Display_P3, A98_RGB, ProPhoto_RGB, Rec_2020
    )
    CS_MAP = {obj.space(): obj for obj in SUPPORTED}

    def __init__(self, color, data=None, filters=None):
        """Initialize."""

        self._attach(self._parse(color, data, filters))

    def __repr__(self):
        """Representation."""

        return repr(self._color)

    __str__ = __repr__

    def _attach(self, color):
        """Attach the this objects convert space to the color."""

        self._color = color
        self._color.spaces = {k: v for k, v in self.CS_MAP.items()}

    @classmethod
    def _parse(cls, color, data=None, filters=None):
        """Parse the color."""

        obj = None
        if data is not None:
            filters = set(filters) if filters is not None else set()
            for space in cls.SUPPORTED:
                s = color.lower()
                if space.SPACE == s and (not filters or s in filters):
                    obj = space(data)
                    return obj
        elif isinstance(color, Color):
            if not filters or color.space() in filters:
                obj = cls.CS_MAP[color.space()](color._color)
        else:
            m = cls._match(color, fullmatch=True, filters=filters)
            if m is None:
                raise ValueError("'{}' is not a valid color".format(color))
            obj = m.color
        if obj is None:
            raise ValueError("Could not process the provided color")
        return obj

    @classmethod
    def _match(cls, string, start=0, fullmatch=False, filters=None):
        """Match a color in a buffer and return a color object."""

        filters = set(filters) if filters is not None else set()

        for space in cls.SUPPORTED:
            if space.SPACE not in cls.CS_MAP or (filters and space.SPACE not in filters):
                continue
            value, match_end = space.match(string, start, fullmatch)
            if value is not None:
                color = space(value)
                return ColorMatch(color, start, match_end)
        return None

    @classmethod
    def match(cls, string, start=0, fullmatch=False, filters=None):
        """Match color."""

        obj = cls._match(string, start, fullmatch, filters)
        if obj is not None:
            obj.color = cls(obj.color.space(), obj.color._channels + [obj.color.alpha])
        return obj

    def space(self):
        """The current color space."""

        return self._color.space()

    def coords(self, scale=util.DEF_PREC):
        """Coordinates."""

        return self._color.coords(scale=scale)

    @classmethod
    def new(cls, color, data=None, filters=None):
        """Create new color object."""

        return cls(color, data, filters)

    def clone(self):
        """Clone."""

        clone = self._color.clone()
        return type(self)(clone.space(), clone._channels + [clone.alpha])

    def convert(self, space, fit=False):
        """Convert."""

        obj = self._color.convert(space, fit)
        return type(self)(obj.space(), obj._channels + [obj.alpha])

    def update(self, color, data=None, filters=None):
        """Update the existing color space with the provided color."""

        obj = self._parse(color, data, filters)
        self._color.update(obj)
        return self

    def mutate(self, color, data=None, filters=None):
        """Mutate the current color to a new color."""

        self._attach(self._parse(color, data, filters))
        return self

    def to_string(self, **kwargs):
        """To string."""

        return self._color.to_string(**kwargs)

    def get(self, name):
        """Get channel."""

        return self._color.get(name)

    def set(self, name, value):  # noqa: A003
        """Set channel."""

        self._color.set(name, value)
        return self

    def is_achromatic(self):
        """Check if color is is_achromatic."""

        return self._color.is_achromatic()

    def delta(self, color):
        """Get distance between this color and the provided color."""

        return self._color.delta(color._color)

    def luminance(self):
        """Get color's luminance."""

        return self._color.luminance()

    def contrast_ratio(self, color):
        """Compare the contrast ration of this color and the provided color."""

        return self._color(color._color)

    def alpha_composite(self, background=None):
        """Apply the given transparency with the given background."""

        if background is not None:
            background = background._color

        self._color.alpha_composite(background)
        return self

    def mix(self, color, percent, alpha=False, space="lch"):
        """Mix the two colors."""

        self._color.mix(color._color, percent, alpha=alpha, space=space)
        return self

    def __getattr__(self, name):
        """Get attribute."""

        if name != '_color':
            return getattr(self._color, name)

    def __setattr__(self, name, value):
        """Set attribute."""

        try:
            if name in self._color.CHANNEL_NAMES:
                setattr(self._color, name, value)
        except AttributeError:
            super().__setattr__(name, value)
