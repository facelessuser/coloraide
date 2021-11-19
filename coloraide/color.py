"""Colors."""
import abc
import functools
from . import cat
from . import distance
from . import convert
from . import gamut
from . import compositing
from . import interpolate
from . import util
from .util import Vector, MutableVector, ColorInput
from .spaces import Space, Cylindrical
from .spaces.hsv import HSV
from .spaces.srgb.css import SRGB
from .spaces.srgb_linear import SRGBLinear
from .spaces.hsl.css import HSL
from .spaces.hwb.css import HWB
from .spaces.lab.css import Lab
from .spaces.lch.css import Lch
from .spaces.lab_d65 import LabD65
from .spaces.lch_d65 import LchD65
from .spaces.display_p3 import DisplayP3
from .spaces.a98_rgb import A98RGB
from .spaces.prophoto_rgb import ProPhotoRGB
from .spaces.rec2020 import Rec2020
from .spaces.xyz import XYZ
from .spaces.xyz_d50 import XYZD50
from .spaces.oklab import Oklab
from .spaces.oklch import Oklch
from .spaces.jzazbz import Jzazbz
from .spaces.jzczhz import JzCzhz
from .spaces.ictcp import ICtCp
from .spaces.din99o import Din99o
from .spaces.din99o_lch import Din99oLch
from .spaces.luv import Luv
from .spaces.lchuv import Lchuv
from .spaces.luv_d65 import LuvD65
from .spaces.lchuv_d65 import LchuvD65
from .spaces.okhsl import Okhsl
from .spaces.okhsv import Okhsv
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
from .gamut.fit_lch_chroma import LchChroma
from typing import Union, Sequence, Dict, List, Optional, Any, cast, Callable, Set, Tuple, Type, Mapping

SUPPORTED_DE = (
    DE76, DE94, DECMC, DE2000, DEITP, DE99o, DEZ, DEHyAB
)

SUPPORTED_SPACES = (
    HSL, HWB, Lab, Lch, LabD65, LchD65, SRGB, SRGBLinear, HSV,
    DisplayP3, A98RGB, ProPhotoRGB, Rec2020, XYZ, XYZD50,
    Oklab, Oklch, Jzazbz, JzCzhz, ICtCp, Din99o, Din99oLch, Luv, Lchuv,
    LuvD65, LchuvD65, Okhsl, Okhsv
)

SUPPORTED_FIT = (
    LchChroma,
)


class ColorMatch:
    """Color match object."""

    def __init__(self, color: 'Color', start: int, end: int) -> None:
        """Initialize."""

        self.color = color
        self.start = start
        self.end = end

    def __str__(self) -> str:  # pragma: no cover
        """String."""

        return "ColorMatch(color={!r}, start={}, end={})".format(self.color, self.start, self.end)

    __repr__ = __str__


class BaseColor(abc.ABCMeta):
    """Ensure on subclass that the subclass has new instances of mappings."""

    def __init__(cls, name: str, bases: Tuple[object, ...], clsdict: Dict[str, Any]) -> None:
        """Copy mappings on subclass."""

        if len(cls.mro()) > 2:
            cls.CS_MAP = cls.CS_MAP.copy()  # type: Dict[str, Type[Space]]
            cls.DE_MAP = cls.DE_MAP.copy()  # type: Dict[str, Type[DeltaE]]
            cls.FIT_MAP = cls.FIT_MAP.copy()  # type: Dict[str, Type[Fit]]


class Color(metaclass=BaseColor):
    """Color class object which provides access and manipulation of color spaces."""

    CS_MAP = {}  # type: Dict[str, Type[Space]]
    DE_MAP = {}  # type: Dict[str, Type[DeltaE]]
    FIT_MAP = {}  # type: Dict[str, Type[Fit]]
    PRECISION = util.DEF_PREC
    FIT = util.DEF_FIT
    DELTA_E = util.DEF_DELTA_E
    CHROMATIC_ADAPTATION = 'bradford'

    # It is highly unlikely that a user would ever need to override this, but
    # just in case, it is exposed, but undocumented.
    #
    # This is meant to prevent infinite loops in the event that a user registers
    # poorly crafted color spaces with circular convert linkage or somehow doesn't
    # resolve to XYZ. 10 is a generous size as our current largest iteration chain
    # is 6, and increasing that past 10 seems highly unlikely:
    #    XYZ -> sRGB Linear -> sRGB -> HSL -> HSV -> HWB
    _MAX_CONVERT_ITERATIONS = 10

    def __init__(
        self,
        color: ColorInput,
        data: Optional[Vector] = None,
        alpha: float = util.DEF_ALPHA,
        *,
        filters: Optional[Sequence[str]] = None,
        **kwargs: Any
    ) -> None:
        """Initialize."""

        self._attach(self._parse(color, data, alpha, filters=filters, **kwargs))

    def __dir__(self) -> Sequence[str]:
        """Get attributes for `dir()`."""

        attr = cast(List['str'], super().__dir__())
        attr.extend(self._space.CHANNEL_NAMES)
        attr.extend('alpha')
        attr.extend(list(self._space.CHANNEL_ALIASES.keys()))
        attr.extend(['delta_e_{}'.format(name) for name in self.DE_MAP.keys()])
        return attr

    def __eq__(self, other: Any) -> bool:
        """Compare equal."""

        return (
            type(other) == type(self) and
            other.space() == self.space() and
            util.cmp_coords(other.coords() + [other.alpha], self.coords() + [self.alpha])
        )

    def _parse(
        self,
        color: ColorInput,
        data: Optional[Vector] = None,
        alpha: float = util.DEF_ALPHA,
        *,
        filters: Optional[Sequence[str]] = None,
        **kwargs: Any
    ) -> Space:
        """Parse the color."""

        obj = None
        if isinstance(color, str):
            if data is not None:
                for space, space_class in self.CS_MAP.items():
                    s = color.lower()
                    if space == s and (not filters or s in filters):
                        num_channels = len(space_class.CHANNEL_NAMES)
                        if len(data) < num_channels:
                            data = list(data) + [util.NaN] * (num_channels - len(data))
                        obj = space_class(data[:num_channels], alpha)
                        break
            else:
                m = self._match(color, fullmatch=True, filters=filters)
                if m is None:
                    raise ValueError("'{}' is not a valid color".format(color))
                obj = m[0]
        elif isinstance(color, Color):
            if not filters or color.space() in filters:
                obj = self.CS_MAP[color.space()](color._space)
        elif isinstance(color, Mapping):
            space = color['space']
            if not filters or space in filters:
                cs = self.CS_MAP[space]
                coords = [color[name] for name in cs.CHANNEL_NAMES]
                alpha = color.get('alpha', 1)
                obj = cs(coords, alpha)
        else:
            raise TypeError("'{}' is an unrecognized type".format(type(color)))

        if obj is None:
            raise ValueError("Could not process the provided color")
        return obj

    @classmethod
    def _match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = False,
        filters: Optional[Sequence[str]] = None
    ) -> Optional[Tuple['Space', int, int]]:
        """
        Match a color in a buffer and return a color object.

        This must return the color space, not the Color object.
        """

        filter_set = set(filters) if filters is not None else set()  # type: Set[str]

        for space, space_class in cls.CS_MAP.items():
            if filter_set and space not in filter_set:
                continue
            m = space_class.match(string, start, fullmatch)
            if m is not None:
                color = space_class(*m[0])
                return color, start, m[1]
        return None

    @classmethod
    def match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = False,
        *,
        filters: Optional[Sequence[str]] = None
    ) -> Optional[ColorMatch]:
        """Match color."""

        m = cls._match(string, start, fullmatch, filters=filters)
        if m is not None:
            color = m[0]
            return ColorMatch(cls(color.NAME, color.coords(), color.alpha), m[1], m[2])
        return None

    @classmethod
    def register(
        cls,
        plugin: Union[Type[Fit], Type[DeltaE], Type[Space], Sequence[Any]],
        overwrite: bool = False
    ) -> None:
        """Register the hook."""

        if not isinstance(plugin, Sequence):
            plugin = [plugin]

        mapping = None  # type: Optional[Union[Dict[str, Type[Fit]], Dict[str, Type[DeltaE]], Dict[str, Type[Space]]]]
        for p in plugin:
            if issubclass(p, Space):
                name = p.NAME
                value = p
                mapping = cls.CS_MAP
            elif issubclass(p, DeltaE):
                name = p.NAME
                value = p
                mapping = cls.DE_MAP
            elif issubclass(p, Fit):
                name = p.NAME
                value = p
                mapping = cls.FIT_MAP
                if name == 'clip':
                    raise ValueError("'{}' is a reserved name for gamut mapping/reduction and cannot be overridden")
            else:
                raise TypeError("Cannot register plugin of type '{}'".format(type(p)))

            if name != "*" and name not in mapping or overwrite:
                mapping[name] = value
            else:
                raise ValueError("A plugin with the name of '{}' already exists or is not allowed".format(name))

    @classmethod
    def deregister(cls, plugin: Union[str, Sequence[str]], silent: bool = False) -> None:
        """Deregister a plugin by name of specified plugin type."""

        if isinstance(plugin, str):
            plugin = [plugin]

        mapping = None  # type: Optional[Union[Dict[str, Type[Fit]], Dict[str, Type[DeltaE]], Dict[str, Type[Space]]]]
        for p in plugin:
            if p == '*':
                cls.CS_MAP.clear()
                cls.DE_MAP.clear()
                cls.FIT_MAP.clear()
                return

            ptype, name = p.split(':', 1)
            if ptype == 'space':
                mapping = cls.CS_MAP
            elif ptype == "delta-e":
                mapping = cls.DE_MAP
            elif ptype == "fit":
                mapping = cls.FIT_MAP
                if name == 'clip':
                    raise ValueError("'{}' is a reserved name gamut mapping/reduction and cannot be removed")
            else:
                raise ValueError("The plugin category of '{}' is not recognized".format(ptype))

            if name == '*':
                mapping.clear()
            elif name in mapping:
                del mapping[name]
            elif not silent:
                raise ValueError("A plugin of name '{}' under category '{}' could not be found".format(name, ptype))

    def to_dict(self) -> Mapping[str, Any]:
        """Return color as a data object."""

        data = {'space': self.space()}  # type: Dict[str, Any]
        coords = self.coords()
        for i, name in enumerate(self._space.CHANNEL_NAMES, 0):
            data[name] = coords[i]
        data['alpha'] = self.alpha
        return data

    def normalize(self) -> 'Color':
        """Normalize the color."""

        coords, alpha = self._space.null_adjust(self.coords(), self.alpha)
        return self.mutate(self.space(), coords, alpha)

    def is_nan(self, name: str) -> bool:
        """Check if channel is NaN."""

        return util.is_nan(self.get(name))

    def _is_this_color(self, obj: Any) -> bool:
        """Test if the input is "this" Color, not a subclass."""

        return type(obj) is type(self)

    def _is_color(self, obj: Any) -> bool:
        """Test if the input is a Color."""

        return isinstance(obj, Color)

    def _attach(self, space: Space) -> None:
        """Attach the this objects convert space to the color."""

        self._space = space

    def _handle_color_input(self, color: ColorInput) -> 'Color':
        """Handle color input."""

        if (
            isinstance(color, str) or
            isinstance(color, Mapping) or
            (self._is_color(color) and not self._is_this_color(color))
        ):
            return self.new(color)
        elif not self._is_color(color):
            raise TypeError("Unexpected type '{}'".format(type(color)))
        return color

    def space(self) -> str:
        """The current color space."""

        return self._space.NAME

    def coords(self) -> MutableVector:
        """Coordinates."""

        return self._space.coords()

    def new(
        self,
        color: ColorInput,
        data: Optional[Vector] = None,
        alpha: float = util.DEF_ALPHA,
        *,
        filters: Optional[Sequence[str]] = None,
        **kwargs: Any
    ) -> 'Color':
        """
        Create new color object.

        TODO: maybe allow `currentcolor` here? It would basically clone the current object.
        """

        return type(self)(color, data, alpha, filters=filters, **kwargs)

    def clone(self) -> 'Color':
        """Clone."""

        return self.new(self.space(), self.coords(), self.alpha)

    def chromatic_adaptation(self, w1: str, w2: str, xyz: Vector) -> MutableVector:
        """Apply chromatic adaption to XYZ coordinates."""

        return cat.chromatic_adaptation(w1, w2, xyz, method=self.CHROMATIC_ADAPTATION)

    def convert(self, space: str, *, fit: bool = False, in_place: bool = False) -> 'Color':
        """Convert to color space."""

        space = space.lower()

        if fit:
            method = None if not isinstance(fit, str) else fit
            if not self.in_gamut(space, tolerance=0.0):
                converted = self.convert(space, in_place=in_place)
                return converted.fit(space, method=method, in_place=True)

        coords = convert.convert(self, space)

        return self.mutate(space, coords, self.alpha) if in_place else self.new(space, coords, self.alpha)

    def mutate(
        self,
        color: ColorInput,
        data: Optional[Vector] = None,
        alpha: float = util.DEF_ALPHA,
        *,
        filters: Optional[Sequence[str]] = None,
        **kwargs: Any
    ) -> 'Color':
        """Mutate the current color to a new color."""

        c = self._parse(color, data=data, alpha=alpha, filters=filters, **kwargs)
        self._attach(c)
        return self

    def update(
        self,
        color: Union['Color', str, Mapping[str, Any]],
        data: Optional[Vector] = None,
        alpha: float = util.DEF_ALPHA,
        *,
        filters: Optional[Sequence[str]] = None,
        **kwargs: Any
    ) -> 'Color':
        """Update the existing color space with the provided color."""

        c = self._parse(color, data=data, alpha=alpha, filters=filters, **kwargs)
        space = self.space()
        self._attach(c)
        if c.NAME != space:
            self.convert(space, in_place=True)
        return self

    def to_string(self, **kwargs: Any) -> str:
        """To string."""

        return self._space.to_string(self, **kwargs)

    def __repr__(self) -> str:
        """Representation."""

        return repr(self._space)

    __str__ = __repr__

    def white(self) -> MutableVector:
        """Get the white point."""

        return util.xy_to_xyz(self._space.white())

    def uv(self, mode: str = '1976') -> MutableVector:
        """Convert to `xy`."""

        uv = None
        if mode == '1976':
            xyz = self.convert('xyz')
            coords = self.chromatic_adaptation(xyz._space.WHITE, self._space.WHITE, xyz.coords())
            uv = util.xyz_to_uv(coords)
        elif mode == '1960':
            uv = util.xy_to_uv_1960(self.xy())
        else:
            raise ValueError("'mode' must be either '1960' or '1976' (default), not '{}'".format(mode))
        return uv

    def xy(self) -> MutableVector:
        """Convert to `xy`."""

        xyz = self.convert('xyz')
        coords = self.chromatic_adaptation(xyz._space.WHITE, self._space.WHITE, xyz.coords())
        return util.xyz_to_xyY(coords, self._space.white())[:2]

    def clip(self, space: Optional[str] = None, *, in_place: bool = False) -> 'Color':
        """Clip the color channels."""

        if space is None:
            space = self.space()

        this = self.clone() if not in_place else self

        # Convert to desired space
        c = self.convert(space)

        # If we are perfectly in gamut, don't waste time clipping.
        if c.in_gamut(tolerance=0.0):
            if isinstance(c._space, Cylindrical):
                name = c._space.hue_name()
                c.set(name, util.constrain_hue(c.get(name)))
        else:
            c._space._coords = gamut.clip_channels(c)
        c.normalize()

        # Adjust "this" color
        return this.update(c)

    def fit(self, space: Optional[str] = None, *, method: Optional[str] = None, in_place: bool = False) -> 'Color':
        """Fit the gamut using the provided method."""

        # Dedicated clip method.
        if method == 'clip' or (method is None and self.FIT == "clip"):
            return self.clip(space, in_place=in_place)

        if space is None:
            space = self.space()

        if method is None:
            method = self.FIT

        this = self.clone() if not in_place else self

        # Select appropriate mapping algorithm
        if method in self.FIT_MAP:
            func = self.FIT_MAP[method].fit
        else:
            # Unknown fit method
            raise ValueError("'{}' gamut mapping is not currently supported".format(method))

        # Convert to desired space
        c = self.convert(space)

        # If we are perfectly in gamut, don't waste time fitting, just normalize hues.
        # If out of gamut, apply mapping/clipping/etc.
        if c.in_gamut(tolerance=0.0):
            if isinstance(c._space, Cylindrical):
                name = c._space.hue_name()
                c.set(name, util.constrain_hue(c.get(name)))
        else:
            # Doesn't seem to be an easy way that `mypy` can know whether this is the ABC class or not
            c._space._coords = func(c)
        c.normalize()

        # Adjust "this" color
        return this.update(c)

    def in_gamut(self, space: Optional[str] = None, *, tolerance: float = util.DEF_FIT_TOLERANCE) -> bool:
        """Check if current color is in gamut."""

        space = space.lower() if space is not None else self.space()

        # Check gamut in the provided space
        if space is not None and space != self.space():
            c = self.convert(space)
            return c.in_gamut(tolerance=tolerance)

        # Check the color space specified for gamut checking.
        # If it proves to be in gamut, we will then test if the current
        # space is constrained properly.
        if self._space.GAMUT_CHECK is not None:
            c = self.convert(self._space.GAMUT_CHECK)
            if not c.in_gamut(tolerance=tolerance):
                return False

        return gamut.verify(self, tolerance)

    def mask(self, channel: Union[str, Sequence[str]], *, invert: bool = False, in_place: bool = False) -> 'Color':
        """Mask color channels."""

        this = self if in_place else self.clone()
        aliases = self._space.CHANNEL_ALIASES
        masks = set(
            [aliases.get(channel, channel)] if isinstance(channel, str) else [aliases.get(c, c) for c in channel]
        )
        for name in (self._space.CHANNEL_NAMES + ('alpha',)):
            if (not invert and name in masks) or (invert and name not in masks):
                this.set(name, util.NaN)
        return this

    def steps(
        self,
        color: Union[Union[ColorInput, interpolate.Piecewise], Sequence[Union[ColorInput, interpolate.Piecewise]]],
        *,
        steps: int = 2,
        max_steps: int = 1000,
        max_delta_e: float = 0,
        **interpolate_args: Any
    ) -> List['Color']:
        """
        Discrete steps.

        This is built upon the interpolate function, and will return a list of
        colors containing a minimum of colors equal to `steps` or steps as specified
        derived from the `max_delta_e` parameter (whichever is greatest).

        Number of colors can be capped with `max_steps`.

        Default delta E method used is delta E 76.
        """

        return self.interpolate(color, **interpolate_args).steps(steps, max_steps, max_delta_e)

    def mix(
        self,
        color: ColorInput,
        percent: float = util.DEF_MIX,
        *,
        in_place: bool = False,
        **interpolate_args: Any
    ) -> 'Color':
        """
        Mix colors using interpolation.

        This uses the interpolate method to find the center point between the two colors.
        The basic mixing logic is outlined in the CSS level 5 draft.
        """

        if not self._is_color(color) and not isinstance(color, (str, interpolate.Piecewise, Mapping)):
            raise TypeError("Unexpected type '{}'".format(type(color)))
        mixed = self.interpolate(color, **interpolate_args)(percent)
        return self.mutate(mixed) if in_place else mixed

    def interpolate(
        self,
        color: Union[Union[ColorInput, interpolate.Piecewise], Sequence[Union[ColorInput, interpolate.Piecewise]]],
        *,
        space: str = "lab",
        out_space: Optional[str] = None,
        stop: float = 0,
        progress: Optional[Callable[..., float]] = None,
        hue: str = util.DEF_HUE_ADJ,
        premultiplied: bool = False
    ) -> interpolate.Interpolator:
        """
        Return an interpolation function.

        The function will return an interpolation function that accepts a value (which should
        be in the range of [0..1] and will return a color based on that value.

        While we use NaNs to mask off channels when doing the interpolation, we do not allow
        arbitrary specification of NaNs by the user, they must specify channels via `adjust`
        if they which to target specific channels for mixing. Null hues become NaNs before
        mixing occurs.
        """

        space = space.lower()
        out_space = self.space() if out_space is None else out_space.lower()

        # A piecewise object was provided, so treat it as such,
        # or we've changed the stop of the base color, so run it through piecewise.
        if (
            isinstance(color, interpolate.Piecewise) or
            (stop != 0 and (isinstance(color, (str, Mapping)) or self._is_color(color)))
        ):
            color = cast(Sequence[Union['Color', str, Mapping[str, Any], interpolate.Piecewise]], [color])

        if not isinstance(color, str) and isinstance(color, Sequence):
            # We have a sequence, so use piecewise interpolation
            colors = list(color)
            colors.insert(0, interpolate.Piecewise(self, stop=stop))
            return interpolate.color_piecewise_lerp(
                colors,
                space,
                out_space,
                progress,
                hue,
                premultiplied
            )
        else:
            # We have a sequence, so use piecewise interpolation
            return interpolate.color_lerp(
                self,
                color,
                space,
                out_space,
                progress,
                hue,
                premultiplied
            )

    def compose(
        self,
        backdrop: Union[ColorInput, Sequence[ColorInput]],
        *,
        blend: Union[str, bool] = True,
        operator: Union[str, bool] = True,
        space: Optional[str] = None,
        out_space: Optional[str] = None,
        in_place: bool = False
    ) -> 'Color':
        """Blend colors using the specified blend mode."""

        if not isinstance(backdrop, str) and isinstance(backdrop, Sequence):
            bcolor = [self._handle_color_input(c) for c in backdrop]
        else:
            bcolor = [self._handle_color_input(backdrop)]

        color = compositing.compose(self, bcolor, blend, operator, space)

        outspace = self.space() if out_space is None else out_space.lower()
        return (
            self.mutate(color.convert(outspace)) if in_place else color.convert(outspace)
        ).normalize()

    def delta_e(
        self,
        color: ColorInput,
        *,
        method: Optional[str] = None,
        **kwargs: Any
    ) -> float:
        """Delta E distance."""

        color = self._handle_color_input(color)
        if method is None:
            method = self.DELTA_E

        algorithm = method.lower()

        try:
            return self.DE_MAP[algorithm].distance(self, color, **kwargs)
        except KeyError:
            raise ValueError("'{}' is not currently a supported distancing algorithm.".format(algorithm))

    def distance(self, color: ColorInput, *, space: str = "lab") -> float:
        """Delta."""

        color = self._handle_color_input(color)
        return distance.distance_euclidean(self, color, space=space)

    def luminance(self) -> float:
        """Get color's luminance."""

        return cast(float, self.convert("xyz").y)

    def contrast(self, color: ColorInput) -> float:
        """Compare the contrast ratio of this color and the provided color."""

        color = self._handle_color_input(color)
        lum1 = self.luminance()
        lum2 = color.luminance()
        return (lum1 + 0.05) / (lum2 + 0.05) if (lum1 > lum2) else (lum2 + 0.05) / (lum1 + 0.05)

    def get(self, name: str) -> float:
        """Get channel."""

        # Handle space.attribute
        if '.' in name:
            parts = name.split('.')
            if len(parts) != 2:
                raise ValueError("Could not resolve attribute '{}'".format(name))
            obj = self.convert(parts[0])
            return obj.get(parts[1])

        return self._space.get(name)

    def set(self, name: str, value: Union[float, Callable[..., float]]) -> 'Color':  # noqa: A003
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
        self._space.set(name, value(self._space.get(name)) if callable(value) else value)

        return self

    def __getattr__(self, name: str) -> Any:
        """Get attribute."""

        if name.startswith('delta_e_'):
            de = name[8:]
            if de in self.DE_MAP:
                return functools.partial(self.delta_e, method=de)

        # Don't test `_space` as it is used to get Space channel attributes.
        elif name != "_space":
            try:
                return self._space.get(name)
            except AttributeError:
                pass

        # Get attributes from Color class.
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute."""

        try:
            # See if we need to set the space specific channel attributes.
            self._space.set(name, value)
            return
        except AttributeError:
            pass
        # Set all attributes on the Color class.
        super().__setattr__(name, value)


Color.register(SUPPORTED_SPACES + SUPPORTED_DE + SUPPORTED_FIT)
