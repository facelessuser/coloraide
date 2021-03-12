"""Colors."""
from .hsv import HSV
from .srgb import SRGB
from .srgb_linear import SRGB_Linear
from .hsl import HSL
from .hwb import HWB
from .lab import LAB
from .lch import LCH
from .display_p3 import Display_P3
from .a98_rgb import A98_RGB
from .prophoto_rgb import ProPhoto_RGB
from .rec2020 import Rec2020
from .xyz import XYZ
from .. import util
import functools

DEF_FIT = "lch-chroma"
DEF_DELTA_E = "76"

SUPPORTED = (
    HSL, HWB, LAB, LCH, SRGB, SRGB_Linear, HSV,
    Display_P3, A98_RGB, ProPhoto_RGB, Rec2020, XYZ
)


def _interpolate(percent, color=None, interp=None):
    """Wrapper for interpolate."""

    obj = interp(percent)
    return color.new(obj.space(), obj.coords(), obj.alpha)


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
    """Color class object which provides access and manipulation of color spaces."""

    CS_MAP = {obj.space(): obj for obj in SUPPORTED}

    PRECISION = util.DEF_PREC
    FIT = util.DEF_FIT
    DELTA_E = util.DEF_DELTA_E

    def __init__(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
        """Initialize."""

        self._attach(self._parse(color, data, alpha, filters=filters, **kwargs))

    def __eq__(self, other):
        """Compare equal."""

        return (
            other.space() == self.space() and
            util.cmp_coords(other.coords(), self.coords()) and
            util.cmp_coords(other.alpha, self.alpha)
        )

    def is_nan(self, name):
        """Check if channel is NaN."""

        return util.is_nan(self.get(name))

    def _attach(self, color):
        """Attach the this objects convert space to the color."""

        self._color = color
        self._color.parent = self

    def _handle_color_input(self, color):
        """Handle color input."""

        if isinstance(color, Color):
            color = color._color
        elif isinstance(color, str):
            color = self.new(color)._color
        else:
            raise TypeError("Unexpected type '{}'".format(type(color)))
        return color

    def _parse(self, color, data=None, alpha=util.DEF_ALPHA, filters=None, **kwargs):
        """Parse the color."""

        obj = None
        if data is not None:
            filters = set(filters) if filters is not None else set()
            for space, space_class in self.CS_MAP.items():
                s = color.lower()
                if space == s and (not filters or s in filters):
                    obj = space_class(data[:space_class.NUM_COLOR_CHANNELS] + [alpha])
                    return obj
        elif isinstance(color, Color):
            if not filters or color.space() in filters:
                obj = self.CS_MAP[color.space()](color._color)
        else:
            m = self._match(color, fullmatch=True, filters=filters)
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
    def match(cls, string, start=0, fullmatch=False, *, filters=None):
        """Match color."""

        obj = cls._match(string, start, fullmatch, filters=filters)
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
    def new(cls, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
        """Create new color object."""

        return cls(color, data, alpha, filters=filters, **kwargs)

    def clone(self):
        """Clone."""

        clone = self._color.clone()
        return self.new(clone.space(), clone.coords(), clone.alpha)

    def convert(self, space, *, fit=False, in_place=False):
        """Convert."""

        obj = self._color.convert(space, fit=fit)
        if in_place:
            return self._attach(obj)
        return type(self)(obj.space(), obj.coords(), obj.alpha)

    def update(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
        """Update the existing color space with the provided color."""

        clone = self.clone()
        obj = self._parse(color, data, alpha, filters=filters, **kwargs)
        clone._attach(obj)
        self._color.update(obj)
        return self

    def mutate(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
        """Mutate the current color to a new color."""

        self._attach(self._parse(color, data, alpha, filters=filters, **kwargs))
        return self

    def to_string(self, **kwargs):
        """To string."""

        return self._color.to_string(**kwargs)

    def __repr__(self):
        """Representation."""

        return repr(self._color)

    __str__ = __repr__

    def luminance(self):
        """Get color's luminance."""

        return self._color.luminance()

    def contrast(self, color):
        """Compare the contrast ratio of this color and the provided color."""

        color = self._handle_color_input(color)
        return self._color.contrast(color)

    def distance(self, color, *, space=util.DEF_DISTANCE_SPACE):
        """Get distance between this color and the provided color."""

        color = self._handle_color_input(color)
        return self._color.distance(color, space=space)

    def delta_e(self, color, *, method=None, **kwargs):
        """Delta E distance."""

        color = self._handle_color_input(color)
        return self._color.delta_e(color, method=method, **kwargs)

    def overlay(self, background=None, *, space=None, in_place=False):
        """Apply the given transparency with the given background."""

        background = self._handle_color_input(background)
        obj = self._color.overlay(background, space=space, in_place=in_place)

        if not in_place:
            return self.new(obj.space(), obj.coords(), obj.alpha)
        return self

    def interpolate(
        self, color, *, space="lab", out_space=None, progress=None, adjust=None, hue=util.DEF_HUE_ADJ,
        premultiplied=False
    ):
        """Interpolate."""

        color = self._handle_color_input(color)
        interp = self._color.interpolate(
            color, space=space, progress=progress, out_space=None, adjust=adjust, hue=hue, premultiplied=premultiplied
        )
        return functools.partial(_interpolate, color=self.clone(), interp=interp)

    def steps(self, color, *, steps=2, max_steps=1000, max_delta_e=0, **interpolate_args):
        """Interpolate discrete steps."""

        color = self._handle_color_input(color)
        colors = []
        for obj in self._color.steps(
            color, steps=steps, max_steps=max_steps, max_delta_e=max_delta_e, **interpolate_args
        ):
            colors.append(self.new(obj.space(), obj.coords(), obj.alpha))
        return colors

    def mix(self, color, percent=util.DEF_MIX, *, space=None, in_place=False, **interpolate_args):
        """Mix the two colors."""

        color = self._handle_color_input(color)
        obj = self._color.mix(color, percent, space=space, in_place=in_place, **interpolate_args)
        if not in_place:
            return self.new(obj.space(), obj.coords(), obj.alpha)
        return self

    def fit(self, space=None, *, method=None, in_place=False):
        """Fit to gamut."""

        obj = self._color.fit(space, method=method, in_place=in_place)
        if not in_place:
            return self.new(obj.space(), obj.coords(), obj.alpha)
        return self

    def in_gamut(self, space=None, *, tolerance=util.DEF_FIT_TOLERANCE):
        """Check if in gamut."""

        return self._color.in_gamut(space, tolerance=tolerance)

    def get(self, name):
        """Get channel."""

        # Handle space.attribute
        if '.' in name:
            parts = name.split('.')
            if len(parts) != 2:
                raise ValueError("Could not resolve attribute '{}'".format(name))
            obj = self.convert(parts[0])
            return obj.get(parts[1])

        return self._color.get(name)

    def set(self, name, value):  # noqa: A003
        """Set channel."""

        # Handle space.attribute
        if '.' in name:
            parts = name.split('.')
            if len(parts) != 2:
                raise ValueError("Could not resolve attribute '{}'".format(name))
            obj = self.convert(parts[0])
            obj.set(parts[1], value)
            return self.update(obj)

        # Handle a function that modifies the value or a direct value
        if callable(value):
            self.set(name, value(self.get(name)))
        else:
            self._color.set(name, value)
        return self

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
