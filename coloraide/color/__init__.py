"""Colors."""
from collections.abc import Sequence
from . import distance
from . import convert
from . import gamut
from . import compositing
from . import interpolate
from . import contrast
from . import match
from .. import util
from ..spaces.hsv import HSV
from ..spaces.srgb.css import SRGB
from ..spaces.srgb_linear import SRGBLinear
from ..spaces.hsl.css import HSL
from ..spaces.hwb.css import HWB
from ..spaces.lab.css import Lab
from ..spaces.lch.css import Lch
from ..spaces.lab_d65 import LabD65
from ..spaces.lch_d65 import LchD65
from ..spaces.display_p3 import DisplayP3
from ..spaces.a98_rgb import A98RGB
from ..spaces.prophoto_rgb import ProPhotoRGB
from ..spaces.rec2020 import Rec2020
from ..spaces.xyz import XYZ
from ..spaces.xyz_d65 import XYZD65
from ..spaces.oklab import Oklab
from ..spaces.oklch import Oklch
from ..spaces.jzazbz import Jzazbz
from ..spaces.jzczhz import JzCzhz
from ..spaces.ictcp import ICtCp


SUPPORTED = (
    HSL, HWB, Lab, Lch, LabD65, LchD65, SRGB, SRGBLinear, HSV,
    DisplayP3, A98RGB, ProPhotoRGB, Rec2020, XYZ, XYZD65,
    Oklab, Oklch, Jzazbz, JzCzhz, ICtCp
)


class Color(
    convert.Convert,
    gamut.Gamut,
    compositing.Compose,
    interpolate.Interpolate,
    distance.Distance,
    contrast.Contrast,
    match.Match
):
    """Color class object which provides access and manipulation of color spaces."""

    CS_MAP = {obj.space(): obj for obj in SUPPORTED}

    PRECISION = util.DEF_PREC
    FIT = util.DEF_FIT
    DELTA_E = util.DEF_DELTA_E
    CHROMATIC_ADAPTATION = 'bradford'

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

    def _parse(self, color, data=None, alpha=util.DEF_ALPHA, filters=None, **kwargs):
        """Parse the color."""

        obj = None
        if data is not None:
            filters = set(filters) if filters is not None else set()
            for space, space_class in self.CS_MAP.items():
                s = color.lower()
                if space == s and (not filters or s in filters):
                    if len(data) < space_class.NUM_COLOR_CHANNELS:
                        data = list(data) + [util.NaN] * (space_class.NUM_COLOR_CHANNELS - len(data))
                    obj = space_class(data[:space_class.NUM_COLOR_CHANNELS], alpha)
                    return obj
        elif isinstance(color, Color):
            if not filters or color.space() in filters:
                obj = self.CS_MAP[color.space()](color._space)
        else:
            m = self._match(color, fullmatch=True, filters=filters)
            if m is None:
                raise ValueError("'{}' is not a valid color".format(color))
            obj = m.color
        if obj is None:
            raise ValueError("Could not process the provided color")
        return obj

    def is_nan(self, name):
        """Check if channel is NaN."""

        return util.is_nan(self.get(name))

    def _is_this_color(self, obj):
        """Test if the input is "this" Color, not a subclass."""

        return type(obj) is type(self)

    def _is_color(self, obj):
        """Test if the input is a Color."""

        return isinstance(obj, Color)

    def _attach(self, space):
        """Attach the this objects convert space to the color."""

        self._space = space

    def _handle_color_input(self, color, sequence=False):
        """Handle color input."""

        if isinstance(color, str) or (self._is_color(color) and not self._is_this_color(color)):
            color = self.new(color)
        elif sequence and isinstance(color, Sequence):
            color = [self._handle_color_input(c) for c in color]
        elif not self._is_color(color):
            raise TypeError("Unexpected type '{}'".format(type(color)))
        return color

    def space(self):
        """The current color space."""

        return self._space.space()

    def coords(self):
        """Coordinates."""

        return self._space.coords()

    def new(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
        """
        Create new color object.

        TODO: maybe allow `currentcolor` here? It would basically clone the current object.
        """

        return type(self)(color, data, alpha, filters=filters, **kwargs)

    def clone(self):
        """Clone."""

        return self.new(self.space(), self.coords(), self.alpha)

    def to_string(self, **kwargs):
        """To string."""

        return self._space.to_string(self, **kwargs)

    def __repr__(self):
        """Representation."""

        return repr(self._space)

    __str__ = __repr__

    def get(self, name):
        """Get channel."""

        # Handle space.attribute
        if '.' in name:
            parts = name.split('.')
            if len(parts) != 2:
                raise ValueError("Could not resolve attribute '{}'".format(name))
            obj = self.convert(parts[0])
            return obj.get(parts[1])

        return self._space.get(name)

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
            self._space.set(name, value)
        return self

    def __getattr__(self, name):
        """Get attribute."""

        # Don't test `_space` as it is used to get Space channel attributes.
        if name != "_space":
            # Get channel names
            names = set()
            result = getattr(self, "_space")
            if result is not None:
                names = result.CHANNEL_NAMES
            # If requested attribute is a channel name, return the attribute from the Space instance.
            if name in names:
                return getattr(result, name)

    def __setattr__(self, name, value):
        """Set attribute."""

        try:
            # See if we need to set the space specific channel attributes.
            if name in self._space.CHANNEL_NAMES:
                setattr(self._space, name, value)
                return
        except AttributeError:
            pass
        # Set all attributes on the Color class.
        super().__setattr__(name, value)
