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

SUPPORTED = (
    HSL, HWB, LAB, LCH, SRGB, HSV,
    Display_P3, A98_RGB, ProPhoto_RGB, Rec_2020
)


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

    CS_MAP = {obj.space(): obj for obj in SUPPORTED}

    def __init__(self, color, data=None, alpha=util.DEF_ALPHA, filters=None):
        """Initialize."""

        self._attach(self._parse(color, data, alpha, filters))

    def __repr__(self):
        """Representation."""

        return repr(self._color)

    __str__ = __repr__

    def _attach(self, color):
        """Attach the this objects convert space to the color."""

        self._color = color
        self._color.spaces = {k: v for k, v in self.CS_MAP.items()}

    @classmethod
    def _parse(cls, color, data=None, alpha=util.DEF_ALPHA, filters=None):
        """Parse the color."""

        obj = None
        if data is not None:
            filters = set(filters) if filters is not None else set()
            for space, space_class in cls.CS_MAP.items():
                s = color.lower()
                if space == s and (not filters or s in filters):
                    obj = space_class(data[:space_class.NUM_COLOR_CHANNELS] + [alpha])
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
                color = space_class(value)
                return ColorMatch(color, start, match_end)
        return None

    @classmethod
    def match(cls, string, start=0, fullmatch=False, filters=None):
        """Match color."""

        obj = cls._match(string, start, fullmatch, filters)
        if obj is not None:
            obj.color = cls(obj.color.space(), obj.color.coords(), obj.color.alpha)
        return obj

    def space(self):
        """The current color space."""

        return self._color.space()

    def coords(self):
        """Coordinates."""

        return self._color.coords()

    @classmethod
    def new(cls, color, data=None, alpha=util.DEF_ALPHA, filters=None):
        """Create new color object."""

        return cls(color, data, alpha, filters)

    def clone(self):
        """Clone."""

        clone = self._color.clone()
        return type(self)(clone.space(), clone.coords(), clone.alpha)

    def convert(self, space, fit=False):
        """Convert."""

        obj = self._color.convert(space, fit)
        return type(self)(obj.space(), obj.coords(), obj.alpha)

    def update(self, color, data=None, alpha=util.DEF_ALPHA, filters=None):
        """Update the existing color space with the provided color."""

        obj = self._parse(color, data, alpha, filters)
        self._color.update(obj)
        return self

    def mutate(self, color, data=None, alpha=util.DEF_ALPHA, filters=None):
        """Mutate the current color to a new color."""

        self._attach(self._parse(color, data, alpha, filters))
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

        return self._color.contrast_ratio(color._color)

    def alpha_composite(self, background=None, space=None):
        """Apply the given transparency with the given background."""

        if isinstance(background, Color):
            background = background._color
        elif isinstance(background, str):
            background = self.new(background)._color
        else:
            raise TypeError("Unexpected type '{}'".format(type(background)))

        obj = self._color.alpha_composite(background, space)
        return type(self)(obj.space(), obj.coords(), obj.alpha)

    def mix(self, color, percent=util.DEF_MIX, alpha=False, space=None):
        """Mix the two colors."""

        if isinstance(color, type(self)):
            color = color._color
        elif isinstance(color, str):
            color = self.new(color)._color
        else:
            raise TypeError("Unexpected type '{}'".format(type(color)))

        obj = self._color.mix(color, percent, alpha=alpha, space=space)
        return type(self)(obj.space(), obj.coords(), obj.alpha)

    def fit(self, space=None, method=util.DEF_FIT):
        """Fit gamut."""

        self._color.fit(space, method)

    def in_gamut(self, space=None, tolerance=util.DEF_FIT_TOLERANCE):
        """Check if in gamut."""

        return self._color.in_gamut(space, tolerance)

    def __getattr__(self, name):
        """Get attribute."""

        # Don't test `_color` as it is used to get Space channel attributes.
        if name != "_color":
            # Get channel names
            names = set()
            result = getattr(self, "_color")
            if result is not None:
                names = result.CHANNEL_NAMES
            # If requested attribute is a channel name, return the attribute from the Space instance.
            if name in names:
                return getattr(result, name)

    def __setattr__(self, name, value):
        """Set attribute."""

        try:
            # See if we need to set the space specific channel attributes.
            if name in self._color.CHANNEL_NAMES:
                setattr(self._color, name, value)
                return
        except AttributeError:
            pass
        # Set all attributes on the Color class.
        super().__setattr__(name, value)
