"""Colors."""
from collections.abc import Sequence, Mapping
import abc
import functools
from . import distance
from . import convert
from . import gamut
from . import compositing
from . import interpolate
from . import contrast
from . import match
from .. import util
from ..spaces import Space
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
from ..spaces.din99o import Din99o
from ..spaces.din99o_lch import Din99oLch
from ..spaces.luv import Luv
from ..spaces.lchuv import Lchuv
from ..spaces.okhsl import Okhsl
from ..spaces.okhsv import Okhsv
from .distance import DeltaE
from .distance.delta_e_76 import DE76
from .distance.delta_e_94 import DE94
from .distance.delta_e_cmc import DECMC
from .distance.delta_e_2000 import DE2000
from .distance.delta_e_itp import DEITP
from .distance.delta_e_99o import DE99o
from .distance.delta_e_z import DEZ
from .distance.delta_e_hyab import DEHyAB
from .gamut import Fit
from .gamut.lch_chroma import LchChroma
from .gamut.clip import Clip

SUPPORTED_DE = (
    DE76, DE94, DECMC, DE2000, DEITP, DE99o, DEZ, DEHyAB
)

SUPPORTED_SPACES = (
    HSL, HWB, Lab, Lch, LabD65, LchD65, SRGB, SRGBLinear, HSV,
    DisplayP3, A98RGB, ProPhotoRGB, Rec2020, XYZ, XYZD65,
    Oklab, Oklch, Jzazbz, JzCzhz, ICtCp, Din99o, Din99oLch, Luv, Lchuv,
    Okhsl, Okhsv
)

SUPPORTED_FIT = (
    LchChroma, Clip
)


class BaseColor(abc.ABCMeta):
    """Ensure on subclass that the subclass has new instances of mappings."""

    def __init__(cls, name, bases, clsdict):
        """Copy mappings on subclass."""

        if len(cls.mro()) > 2:
            cls.CS_MAP = dict(cls.CS_MAP)
            cls.DE_MAP = dict(cls.DE_MAP)
            cls.FIT_MAP = dict(cls.FIT_MAP)


class Color(
    convert.Convert,
    gamut.Gamut,
    compositing.Compose,
    interpolate.Interpolate,
    distance.Distance,
    contrast.Contrast,
    match.Match,
    metaclass=BaseColor
):
    """Color class object which provides access and manipulation of color spaces."""

    CS_MAP = {}
    DE_MAP = {}
    FIT_MAP = {}
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
        elif isinstance(color, Mapping):
            space = color['space']
            if not filters or space in filters:
                cs = self.CS_MAP[space]
                coords = [color[name] for name in cs.CHANNEL_NAMES[:-1]]
                alpha = color['alpha']
                obj = cs(coords, alpha)
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

    @classmethod
    def register(cls, plugin, overwrite=False):
        """Register the hook."""

        if not isinstance(plugin, Sequence):
            plugin = [plugin]

        for p in plugin:
            if issubclass(p, Space):
                name = p.space()
                value = p
                mapping = cls.CS_MAP
            elif issubclass(p, DeltaE):
                name = p.name()
                value = p.distance
                mapping = cls.DE_MAP
            elif issubclass(p, Fit):
                name = p.name()
                value = p.fit
                mapping = cls.FIT_MAP
            else:
                raise TypeError("Cannot register plugin of type '{}'".format(type(p)))

            if name != "*" and name not in mapping or overwrite:
                mapping[name] = value
            else:
                raise ValueError("A plugin with the name of '{}' already exists or is not allowed".format(name))

    @classmethod
    def deregister(cls, plugin, silent=False):
        """Deregister a plugin by name of specified plugin type."""

        if isinstance(plugin, str):
            plugin = [plugin]

        for p in plugin:
            if p == '*':
                cls.CS_MAP.clear()
                cls.DE_MAP.clear()
                cls.FIT_MAP.clear()
                return

            ptype, name = p.split(':', 1)
            mapping = None
            if ptype == 'space':
                mapping = cls.CS_MAP
            elif ptype == "delta-e":
                mapping = cls.DE_MAP
            elif ptype == "fit":
                mapping = cls.FIT_MAP
            else:
                raise ValueError("The plugin category of '{}' is not recognized".format(ptype))

            if name == '*':
                mapping.clear()
            elif name in mapping:
                del mapping[name]
            elif not silent:
                raise ValueError("A plugin of name '{}' under category '{}' could not be found".format(name, ptype))

    def to_dict(self):
        """Return color as a data object."""

        data = {'space': self.space()}
        coords = self.coords() + [self.alpha]
        for i, name in enumerate(self._space.CHANNEL_NAMES, 0):
            data[name] = coords[i]
        return data

    def normalize(self):
        """Normalize the color."""

        coords, alpha = self._space.null_adjust(self.coords(), self.alpha)
        return self.mutate(self.space(), coords, alpha)

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

    def white(self):
        """Get the white point."""

        return util.xy_to_xyz(self._space.white())

    def uv(self, mode='1976'):
        """Convert to `xy`."""

        uv = None
        if mode == '1976':
            xyz = self.convert('xyz')
            xyz = self.chromatic_adaptation(xyz._space.WHITE, self._space.WHITE, xyz.coords())
            uv = util.xyz_to_uv(xyz)
        elif mode == '1960':
            uv = util.xy_to_uv_1960(self.xy())
        else:
            raise ValueError("'mode' must be either '1960' or '1976' (default), not '{}'".format(mode))
        return uv

    def xy(self):
        """Convert to `xy`."""

        xyz = self.convert('xyz')
        xyz = self.chromatic_adaptation(xyz._space.WHITE, self._space.WHITE, xyz.coords())
        return util.xyz_to_xyY(xyz, self._space.white())[:2]

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

        if name.startswith('delta_e_'):
            de = name[8:]
            if de in self.DE_MAP:
                return functools.partial(getattr(self, 'delta_e'), method=de)

        # Don't test `_space` as it is used to get Space channel attributes.
        elif name != "_space":
            # Get channel names
            result = getattr(self, "_space")
            if result is not None:
                # If requested attribute is a channel name, return the attribute from the Space instance.
                name = result.CHANNEL_ALIASES.get(name, name)
                if name in result.CHANNEL_NAMES:
                    return getattr(result, name)

        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        """Set attribute."""

        try:
            # See if we need to set the space specific channel attributes.
            name = self._space.CHANNEL_ALIASES.get(name, name)
            if name in self._space.CHANNEL_NAMES:
                setattr(self._space, name, value)
                return
        except AttributeError:
            pass
        # Set all attributes on the Color class.
        super().__setattr__(name, value)


Color.register(SUPPORTED_SPACES + SUPPORTED_DE + SUPPORTED_FIT)
