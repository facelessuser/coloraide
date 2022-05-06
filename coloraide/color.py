"""Colors."""
import abc
import functools
from . import distance
from . import convert
from . import gamut
from . import compositing
from . import interpolate
from . import filters
from . import harmonies
from . import util
from . import algebra as alg
from .css import parse
from .types import VectorLike, Vector, ColorInput
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
from .spaces.xyz_d65 import XYZD65
from .spaces.xyz_d50 import XYZD50
from .spaces.oklab.css import Oklab
from .spaces.oklch.css import Oklch
from .spaces.jzazbz import Jzazbz
from .spaces.jzczhz import JzCzhz
from .spaces.ictcp import ICtCp
from .spaces.din99o import Din99o
from .spaces.lch99o import Lch99o
from .spaces.luv import Luv
from .spaces.lchuv import Lchuv
from .spaces.hsluv import HSLuv
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
from .distance.delta_e_ok import DEOK
from .gamut import Fit
from .gamut.fit_lch_chroma import LchChroma
from .gamut.fit_oklch_chroma import OklchChroma
from .gamut.fit_css_color_4 import CssColor4
from .cat import CAT, Bradford, VonKries, XYZScaling, CAT02, CMCCAT97, Sharp, CMCCAT2000, CAT16
from .filters import Filter
from .filters.w3c_filter_effects import Sepia, Brightness, Contrast, Saturate, Opacity, HueRotate, Grayscale, Invert
from .filters.cvd import Protan, Deutan, Tritan
from .types import Plugin
from typing import overload, Union, Sequence, Dict, List, Optional, Any, cast, Callable, Set, Tuple, Type, Mapping

SUPPORTED_DE = (
    DE76, DE94, DECMC, DE2000, DEITP, DE99o, DEZ, DEHyAB, DEOK
)

SUPPORTED_SPACES = (
    HSL, HWB, Lab, Lch, LabD65, LchD65, SRGB, SRGBLinear, HSV,
    DisplayP3, A98RGB, ProPhotoRGB, Rec2020, XYZD65, XYZD50,
    Oklab, Oklch, Jzazbz, JzCzhz, ICtCp, Din99o, Lch99o, Luv, Lchuv,
    Okhsl, Okhsv, HSLuv
)

SUPPORTED_FIT = (
    LchChroma, OklchChroma, CssColor4
)

SUPPORTED_CAT = (Bradford, VonKries, XYZScaling, CAT02, CMCCAT97, Sharp, CMCCAT2000, CAT16)

SUPPORTED_FILTERS = (
    Sepia, Brightness, Contrast, Saturate, Opacity, HueRotate, Grayscale, Invert, Protan, Deutan, Tritan
)

WARN_COORDS = """
Color channel access has changed. Dynamic channel properties have been deprecated.
Usage of Color.coords() has also been deprecated. All channels can now easily be
accessed with indexing.

- You can index with numbers: Color[0]
- You can index with channel names: Color['red']
- You can slice to get specific color coordinates: Color[:-1]
- You can get all coordinates: Color[:] or list(Color)
- You can even iterate coordinates: [c for c in Color]
- Indexing also supports assignment: Color[0] = 1 or Color[:3] = [1, 1, 1]

Please consider updating usage to utilize this new functionality as Color.coords()
and all other dynamic properties will be removed sometime before the 1.0 release.

These changes were made in an effort to remove unnecessary overhead on every class
attribute get/set operation.
"""

WARN_DE = """
Use of delta_e_<method> is deprecated. Users should use delta_e(color, method=name)
instead.

Please consider updating usage to adhere to this guidance as this functionality will be
removed at some time befor the 1.0 release.

These changes were made in an effort to remove unnecessary overhead on every class
attribute get/set operation.
"""


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


class ColorMeta(abc.ABCMeta):
    """Ensure on subclass that the subclass has new instances of mappings."""

    def __init__(cls, name: str, bases: Tuple[object, ...], clsdict: Dict[str, Any]) -> None:
        """Copy mappings on subclass."""

        # Ensure subclassed Color objects do not use the same plugin mappings
        if len(cls.mro()) > 2:
            cls.CS_MAP = cls.CS_MAP.copy()  # type: Dict[str, Type[Space]]
            cls.DE_MAP = cls.DE_MAP.copy()  # type: Dict[str, Type[DeltaE]]
            cls.FIT_MAP = cls.FIT_MAP.copy()  # type: Dict[str, Type[Fit]]
            cls.CAT_MAP = cls.CAT_MAP.copy()  # type: Dict[str, Type[CAT]]
            cls.FILTER_MAP = cls.FILTER_MAP.copy()  # type: Dict[str, Type[Filter]]

        # Ensure each derived class tracks its own conversion paths for color spaces
        # relative to the installed color space plugins.
        @classmethod  # type: ignore[misc]
        @functools.lru_cache(maxsize=256)
        def _get_convert_chain(
            cls: Type['Color'],
            space: Type['Space'],
            target: str
        ) -> List[Tuple[Type['Space'], Type['Space'], int, bool]]:
            """Resolve a conversion chain, cache it for speed."""

            return convert.get_convert_chain(cls, space, target)

        cls._get_convert_chain = _get_convert_chain


class Color(metaclass=ColorMeta):
    """Color class object which provides access and manipulation of color spaces."""

    CS_MAP = {}  # type: Dict[str, Type[Space]]
    DE_MAP = {}  # type: Dict[str, Type[DeltaE]]
    FIT_MAP = {}  # type: Dict[str, Type[Fit]]
    CAT_MAP = {}  # type: Dict[str, Type[CAT]]
    FILTER_MAP = {}  # type: Dict[str, Type[Filter]]
    PRECISION = util.DEF_PREC
    FIT = util.DEF_FIT
    INTERPOLATE = util.DEF_INTERPOLATE
    DELTA_E = util.DEF_DELTA_E
    HARMONY = util.DEF_HARMONY
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
        data: Optional[VectorLike] = None,
        alpha: float = util.DEF_ALPHA,
        *,
        filters: Optional[Sequence[str]] = None,
        **kwargs: Any
    ) -> None:
        """Initialize."""

        self._space = self._parse(color, data, alpha, filters=filters, **kwargs)

    def __len__(self) -> int:
        """Get number of channels."""

        return len(self._space.CHANNEL_NAMES) + 1

    @overload
    def __getitem__(self, i: Union[str, int]) -> float:  # noqa: D105
        ...

    @overload
    def __getitem__(self, i: slice) -> Vector:  # noqa: D105
        ...

    def __getitem__(self, i: Union[str, int, slice]) -> Union[float, Vector]:
        """Get channels."""

        if isinstance(i, str):
            return self._space.get(i)
        return self._space._coords[i]

    @overload
    def __setitem__(self, i: Union[str, int], v: float) -> None:  # noqa: D105
        ...

    @overload
    def __setitem__(self, i: slice, v: Vector) -> None:  # noqa: D105
        ...

    def __setitem__(self, i: Union[str, int, slice], v: Union[float, Vector]) -> None:
        """Set channels."""

        if isinstance(i, slice):
            for e, name in enumerate((self._space.CHANNEL_NAMES + ('alpha',))[i]):
                setattr(self._space, name, cast(Vector, v)[e])
        elif isinstance(i, int):
            setattr(
                self._space,
                (self._space.CHANNEL_NAMES + ('alpha',))[i],
                v
            )
        else:
            self._space.set(i, cast(float, v))

    def __eq__(self, other: Any) -> bool:
        """Compare equal."""

        return (
            type(other) == type(self) and
            other.space() == self.space() and
            util.cmp_coords(other[:], self[:])
        )

    @classmethod
    def _parse(
        cls,
        color: ColorInput,
        data: Optional[VectorLike] = None,
        alpha: float = util.DEF_ALPHA,
        *,
        filters: Optional[Sequence[str]] = None,
        **kwargs: Any
    ) -> Space:
        """Parse the color."""

        obj = None
        if isinstance(color, str):
            # Parse a color space name and coordinates
            if data is not None:
                s = color
                space_class = cls.CS_MAP.get(s)
                if space_class and (not filters or s in filters):
                    num_channels = len(space_class.CHANNEL_NAMES)
                    if len(data) < num_channels:
                        data = list(data) + [alg.NaN] * (num_channels - len(data))
                    obj = space_class(data[:num_channels], alpha)
            # Parse a CSS string
            else:
                m = cls._match(color, fullmatch=True, filters=filters)
                if m is None:
                    raise ValueError("'{}' is not a valid color".format(color))
                obj = m[0]
        elif isinstance(color, Color):
            # Handle a color instance
            if not filters or color.space() in filters:
                obj = cls.CS_MAP[color.space()](color._space)
        elif isinstance(color, Mapping):
            # Handle a color dictionary
            space = color['space']
            if not filters or space in filters:
                cs = cls.CS_MAP[space]
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

        # Attempt color match
        m = parse.parse_color(string, cls.CS_MAP, start, fullmatch)
        if m is not None:
            if not filter_set or m[0].NAME in filter_set:
                return m[0](*m[1]), start, m[2]
            return None

        # Attempt color space specific match
        for space, space_class in cls.CS_MAP.items():
            if filter_set and space not in filter_set:
                continue
            m2 = space_class.match(string, start, fullmatch)
            if m2 is not None:
                color = space_class(*m2[0])
                return color, start, m2[1]
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
            space = m[0]
            return ColorMatch(cls(space.NAME, space.coords(), space.alpha), m[1], m[2])
        return None

    @classmethod
    def _is_this_color(cls, obj: Any) -> bool:
        """Test if the input is "this" Color, not a subclass."""

        return type(obj) is cls

    @classmethod
    def _is_color(cls, obj: Any) -> bool:
        """Test if the input is a Color."""

        return isinstance(obj, Color)

    @classmethod
    def register(
        cls,
        plugin: Union[Type[Plugin], Sequence[Type[Plugin]]],
        overwrite: bool = False
    ) -> None:
        """Register the hook."""

        reset_convert_cache = False

        if not isinstance(plugin, Sequence):
            plugin = [plugin]

        mapping = None  # type: Optional[Dict[str, Type[Any]]]
        for p in plugin:
            if issubclass(p, Space):
                mapping = cls.CS_MAP
                reset_convert_cache = True
            elif issubclass(p, DeltaE):
                mapping = cls.DE_MAP
            elif issubclass(p, CAT):
                mapping = cls.CAT_MAP
            elif issubclass(p, Filter):
                mapping = cls.FILTER_MAP
            elif issubclass(p, Fit):
                mapping = cls.FIT_MAP
                if p.NAME == 'clip':
                    if reset_convert_cache:  # pragma: no cover
                        cls._get_convert_chain.cache_clear()
                    raise ValueError("'{}' is a reserved name for gamut mapping/reduction and cannot be overridden")
            else:
                if reset_convert_cache:  # pragma: no cover
                    cls._get_convert_chain.cache_clear()
                raise TypeError("Cannot register plugin of type '{}'".format(type(p)))

            name = p.NAME
            value = p

            if name != "*" and name not in mapping or overwrite:
                cast(Dict[str, Type[Plugin]], mapping)[name] = value
            else:
                if reset_convert_cache:  # pragma: no cover
                    cls._get_convert_chain.cache_clear()
                raise ValueError("A plugin with the name of '{}' already exists or is not allowed".format(name))

        if reset_convert_cache:
            cls._get_convert_chain.cache_clear()

    @classmethod
    def deregister(cls, plugin: Union[str, Sequence[str]], silent: bool = False) -> None:
        """Deregister a plugin by name of specified plugin type."""

        reset_convert_cache = False

        if isinstance(plugin, str):
            plugin = [plugin]

        mapping = None  # type: Optional[Dict[str, Type[Any]]]
        for p in plugin:
            if p == '*':
                cls.CS_MAP.clear()
                cls.DE_MAP.clear()
                cls.FIT_MAP.clear()
                cls.CAT_MAP.clear()
                return

            ptype, name = p.split(':', 1)
            if ptype == 'space':
                mapping = cls.CS_MAP
                reset_convert_cache = True
            elif ptype == "delta-e":
                mapping = cls.DE_MAP
            elif ptype == 'cat':
                mapping = cls.CAT_MAP
            elif ptype == 'filter':
                mapping = cls.FILTER_MAP
            elif ptype == "fit":
                mapping = cls.FIT_MAP
                if name == 'clip':
                    if reset_convert_cache:  # pragma: no cover
                        cls._get_convert_chain.cache_clear()
                    raise ValueError("'{}' is a reserved name gamut mapping/reduction and cannot be removed")
            else:
                if reset_convert_cache:  # pragma: no cover
                    cls._get_convert_chain.cache_clear()
                raise ValueError("The plugin category of '{}' is not recognized".format(ptype))

            if name == '*':
                mapping.clear()
            elif name in mapping:
                del mapping[name]
            elif not silent:
                if reset_convert_cache:
                    cls._get_convert_chain.cache_clear()
                raise ValueError("A plugin of name '{}' under category '{}' could not be found".format(name, ptype))

        if reset_convert_cache:
            cls._get_convert_chain.cache_clear()

    def to_dict(self) -> Mapping[str, Any]:
        """Return color as a data object."""

        data = {'space': self.space()}  # type: Dict[str, Any]
        coords = self[:-1]
        for i, name in enumerate(self._space.CHANNEL_NAMES, 0):
            data[name] = coords[i]
        data['alpha'] = self[-1]
        return data

    def normalize(self) -> 'Color':
        """Normalize the color."""

        coords, alpha = self._space.null_adjust(self[:-1], self[-1])
        return self.mutate(self.space(), coords, alpha)

    def is_nan(self, name: str) -> bool:
        """Check if channel is NaN."""

        return alg.is_nan(self.get(name))

    def _handle_color_input(self, color: ColorInput) -> 'Color':
        """Handle color input."""

        if isinstance(color, (str, Mapping)):
            return self.new(color)
        elif self._is_color(color):
            return color if self._is_this_color(color) else self.new(color)
        else:
            raise TypeError("Unexpected type '{}'".format(type(color)))

    def space(self) -> str:
        """The current color space."""

        return self._space.NAME

    def new(
        self,
        color: ColorInput,
        data: Optional[VectorLike] = None,
        alpha: float = util.DEF_ALPHA,
        *,
        filters: Optional[Sequence[str]] = None,
        **kwargs: Any
    ) -> 'Color':
        """Create new color object."""

        return type(self)(color, data, alpha, filters=filters, **kwargs)

    def clone(self) -> 'Color':
        """Clone."""

        return self.new(self.space(), self[:-1], self[-1])

    def convert(self, space: str, *, fit: Union[bool, str] = False, in_place: bool = False) -> 'Color':
        """Convert to color space."""

        if fit:
            method = None if not isinstance(fit, str) else fit
            if not self.in_gamut(space, tolerance=0.0):
                converted = self.convert(space, in_place=in_place)
                return converted.fit(space, method=method, in_place=True)

        if space == self.space():
            return self if in_place else self.clone()

        c = convert.convert(self, space)
        this = self if in_place else self.clone()
        this._space = c

        return this

    def mutate(
        self,
        color: ColorInput,
        data: Optional[VectorLike] = None,
        alpha: float = util.DEF_ALPHA,
        *,
        filters: Optional[Sequence[str]] = None,
        **kwargs: Any
    ) -> 'Color':
        """Mutate the current color to a new color."""

        c = self._parse(color, data=data, alpha=alpha, filters=filters, **kwargs)
        self._space = c
        return self

    def update(
        self,
        color: Union['Color', str, Mapping[str, Any]],
        data: Optional[VectorLike] = None,
        alpha: float = util.DEF_ALPHA,
        *,
        filters: Optional[Sequence[str]] = None,
        **kwargs: Any
    ) -> 'Color':
        """Update the existing color space with the provided color."""

        c = self._parse(color, data=data, alpha=alpha, filters=filters, **kwargs)
        space = self.space()
        self._space = c
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

    def white(self) -> Vector:
        """Get the white point."""

        return util.xy_to_xyz(self._space.white())

    def uv(self, mode: str = '1976') -> Vector:
        """Convert to `xy`."""

        if mode == '1976':
            uv = util.xy_to_uv(self.xy())
        elif mode == '1960':
            uv = util.xy_to_uv_1960(self.xy())
        else:
            raise ValueError("'mode' must be either '1960' or '1976' (default), not '{}'".format(mode))
        return uv

    def xy(self) -> Vector:
        """Convert to `xy`."""

        xyz = self.convert('xyz-d65')
        coords = self.chromatic_adaptation(
            xyz._space.WHITE,
            self._space.WHITE,
            xyz[:-1]
        )
        return util.xyz_to_xyY(coords, self._space.white())[:2]

    @classmethod
    def chromatic_adaptation(
        cls,
        w1: Tuple[float, float],
        w2: Tuple[float, float],
        xyz: VectorLike,
        *,
        method: Optional[str] = None
    ) -> Vector:
        """Chromatic adaptation."""

        try:
            adapter = cls.CAT_MAP[method if method is not None else cls.CHROMATIC_ADAPTATION]
        except KeyError:
            raise ValueError("'{}' is not a supported CAT".format(method))

        return adapter.adapt(w1, w2, xyz)

    def clip(self, space: Optional[str] = None, *, in_place: bool = False) -> 'Color':
        """Clip the color channels."""

        orig_space = self.space()
        if space is None:
            space = self.space()

        # Convert to desired space
        c = self.convert(space, in_place=in_place)

        # If we are perfectly in gamut, don't waste time clipping.
        if c.in_gamut(tolerance=0.0):
            if isinstance(c._space, Cylindrical):
                name = c._space.hue_name()
                c.set(name, util.constrain_hue(c[name]))
        else:
            gamut.clip_channels(c)

        # Adjust "this" color
        return c.convert(orig_space, in_place=True)

    def fit(
        self,
        space: Optional[str] = None,
        *,
        method: Optional[str] = None,
        in_place: bool = False,
        **kwargs: Any
    ) -> 'Color':
        """Fit the gamut using the provided method."""

        # Dedicated clip method.
        orig_space = self.space()
        if method == 'clip' or (method is None and self.FIT == "clip"):
            return self.clip(space, in_place=in_place)

        if space is None:
            space = self.space()

        if method is None:
            method = self.FIT

        # Select appropriate mapping algorithm
        if method in self.FIT_MAP:
            func = self.FIT_MAP[method].fit
        else:
            # Unknown fit method
            raise ValueError("'{}' gamut mapping is not currently supported".format(method))

        # Convert to desired space
        c = self.convert(space, in_place=in_place)

        # If we are perfectly in gamut, don't waste time fitting, just normalize hues.
        # If out of gamut, apply mapping/clipping/etc.
        if c.in_gamut(tolerance=0.0):
            if isinstance(c._space, Cylindrical):
                name = c._space.hue_name()
                c.set(name, util.constrain_hue(c[name]))
        else:
            # Doesn't seem to be an easy way that `mypy` can know whether this is the ABC class or not
            func(c, **kwargs)

        # Adjust "this" color
        return c.convert(orig_space, in_place=True)

    def in_gamut(self, space: Optional[str] = None, *, tolerance: float = util.DEF_FIT_TOLERANCE) -> bool:
        """Check if current color is in gamut."""

        if space is None:
            space = self.space()

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
                this.set(name, alg.NaN)
        return this

    def steps(
        self,
        color: Union[Union[ColorInput, interpolate.Piecewise], Sequence[Union[ColorInput, interpolate.Piecewise]]],
        *,
        steps: int = 2,
        max_steps: int = 1000,
        max_delta_e: float = 0,
        delta_e: Optional[str] = None,
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

        return self.interpolate(color, **interpolate_args).steps(steps, max_steps, max_delta_e, delta_e)

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
        space: Optional[str] = None,
        out_space: Optional[str] = None,
        stop: float = 0,
        progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]] = None,
        hue: str = util.DEF_HUE_ADJ,
        premultiplied: bool = True
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

        if space is None:
            space = self.INTERPOLATE

        if out_space is None:
            out_space = self.space()

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

    def filter(  # noqa: A003
        self,
        name: str,
        amount: Optional[float] = None,
        *,
        space: Optional[str] = None,
        in_place: bool = False,
        **kwargs: Any
    ) -> 'Color':
        """Filter."""

        return filters.filters(self, name, amount, space, in_place, **kwargs)

    def harmony(
        self,
        name: str,
        *,
        space: Optional[str] = None
    ) -> List['Color']:
        """Acquire the specified color harmonies."""

        return harmonies.harmonize(self, name, space)

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

        if out_space is None:
            out_space = self.space()

        color.convert(out_space, in_place=True)
        return self.mutate(color) if in_place else color

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

        try:
            return self.DE_MAP[method].distance(self, color, **kwargs)
        except KeyError:
            raise ValueError("'{}' is not currently a supported distancing algorithm.".format(method))

    def distance(self, color: ColorInput, *, space: str = "lab") -> float:
        """Delta."""

        return distance.distance_euclidean(self, self._handle_color_input(color), space=space)

    def closest(
        self,
        colors: Sequence[ColorInput],
        *,
        method: Optional[str] = None,
        **kwargs: Any
    ) -> 'Color':
        """Find the closest color to the current base color."""

        return distance.closest(self, colors, method=method, **kwargs)

    def luminance(self) -> float:
        """Get color's luminance."""

        return self.convert("xyz-d65")['y']

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
            space, channel = name.split('.', 1)
            obj = self.convert(space)
            return obj._space.get(channel)

        return self._space.get(name)

    def set(  # noqa: A003
        self,
        name: str,
        value: Union[float, Callable[..., float]]
    ) -> 'Color':
        """Set channel."""

        # Handle space.attribute
        if '.' in name:
            space, channel = name.split('.', 1)
            obj = self.convert(space)
            obj._space.set(channel, value(obj._space.get(channel)) if callable(value) else value)
            return self.update(obj)

        # Handle a function that modifies the value or a direct value
        self._space.set(name, value(self._space.get(name)) if callable(value) else value)

        return self

    @util.deprecated(WARN_COORDS)
    def coords(self) -> Vector:  # pragma: no cover
        """
        Coordinates.

        TODO: remove before release of 1.0
        """

        return self._space.coords()

    def __getattr__(self, name: str) -> Any:  # pragma: no cover
        """Get attribute."""

        sc = super()

        # Skip private/protected names
        if not name.startswith('_'):
            # Try color space properties
            try:
                value = sc.__getattribute__('_space').get(name)
                util.warn_deprecated(WARN_COORDS, 3)
                return value
            except AttributeError:
                pass

            # Try delta E methods
            if name.startswith('delta_e_'):
                de = name[8:]
                if de in sc.__getattribute__('DE_MAP'):
                    util.warn_deprecated(WARN_DE, 3)
                    return functools.partial(sc.__getattribute__('delta_e'), method=de)

        # Do the Color class methods
        sc.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:  # pragma: no cover
        """Set attribute."""

        sc = super()

        if not name.startswith('_'):
            try:
                # See if we need to set the space specific channel attributes.
                sc.__getattribute__('_space').set(name, value)
                util.warn_deprecated(WARN_COORDS, 3)
                return
            except AttributeError:  # pragma: no cover
                pass

        # Set all attributes on the Color class.
        sc.__setattr__(name, value)


Color.register(SUPPORTED_SPACES + SUPPORTED_DE + SUPPORTED_FIT + SUPPORTED_CAT + SUPPORTED_FILTERS)
