"""Colors."""
from __future__ import annotations
import abc
import functools
import random
from . import distance
from . import convert
from . import gamut
from . import compositing
from . import interpolate
from . import filters
from . import contrast
from . import harmonies
from . import util
from . import algebra as alg
from itertools import zip_longest as zipl
from .css import parse
from .types import VectorLike, Vector, ColorInput
from .spaces import Space
from .spaces.hsv import HSV
from .spaces.srgb.css import sRGB
from .spaces.srgb_linear import sRGBLinear
from .spaces.hsl.css import HSL
from .spaces.hwb.css import HWB
from .spaces.lab.css import Lab
from .spaces.lch.css import LCh
from .spaces.lab_d65 import LabD65
from .spaces.lch_d65 import LChD65
from .spaces.display_p3 import DisplayP3
from .spaces.display_p3_linear import DisplayP3Linear
from .spaces.a98_rgb import A98RGB
from .spaces.a98_rgb_linear import A98RGBLinear
from .spaces.prophoto_rgb import ProPhotoRGB
from .spaces.prophoto_rgb_linear import ProPhotoRGBLinear
from .spaces.rec2020 import Rec2020
from .spaces.rec2020_linear import Rec2020Linear
from .spaces.xyz_d65 import XYZD65
from .spaces.xyz_d50 import XYZD50
from .spaces.oklab.css import Oklab
from .spaces.oklch.css import OkLCh
from .distance import DeltaE
from .distance.delta_e_76 import DE76
from .distance.delta_e_94 import DE94
from .distance.delta_e_cmc import DECMC
from .distance.delta_e_2000 import DE2000
from .distance.delta_e_hyab import DEHyAB
from .distance.delta_e_ok import DEOK
from .contrast import ColorContrast
from .contrast.wcag21 import WCAG21Contrast
from .gamut import Fit
from .gamut.fit_lch_chroma import LChChroma
from .gamut.fit_oklch_chroma import OkLChChroma
from .cat import CAT, Bradford
from .filters import Filter
from .filters.w3c_filter_effects import Sepia, Brightness, Contrast, Saturate, Opacity, HueRotate, Grayscale, Invert
from .filters.cvd import Protan, Deutan, Tritan
from .interpolate import Interpolator, Interpolate
from .interpolate.bspline import BSpline
from .interpolate.bspline_natural import NaturalBSpline
from .interpolate.monotone import Monotone
from .interpolate.linear import Linear
from .types import Plugin
from typing import overload, Sequence, Optional, Any, cast, Callable, Mapping


class ColorMatch:
    """Color match object."""

    __slots__ = ('color', 'start', 'end')

    def __init__(self, color: Color, start: int, end: int) -> None:
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

    def __init__(cls, name: str, bases: tuple[object, ...], clsdict: dict[str, Any]) -> None:
        """Copy mappings on subclass."""

        # Ensure subclassed Color objects do not use the same plugin mappings
        if len(cls.mro()) > 2:
            cls.CS_MAP = cls.CS_MAP.copy()  # type: dict[str, Space]
            cls.DE_MAP = cls.DE_MAP.copy()  # type: dict[str, DeltaE]
            cls.FIT_MAP = cls.FIT_MAP.copy()  # type: dict[str, Fit]
            cls.CAT_MAP = cls.CAT_MAP.copy()  # type: dict[str, CAT]
            cls.FILTER_MAP = cls.FILTER_MAP.copy()  # type: dict[str, Filter]
            cls.CONTRAST_MAP = cls.CONTRAST_MAP.copy()  # type: dict[str, ColorContrast]
            cls.INTERPOLATE_MAP = cls.INTERPOLATE_MAP.copy()  # type: dict[str, Interpolate]

        # Ensure each derived class tracks its own conversion paths for color spaces
        # relative to the installed color space plugins.
        @classmethod  # type: ignore[misc]
        @functools.lru_cache(maxsize=256)
        def _get_convert_chain(
            cls: type[Color],
            space: Space,
            target: str
        ) -> list[tuple[Space, Space, int, bool]]:
            """Resolve a conversion chain, cache it for speed."""

            return convert.get_convert_chain(cls, space, target)

        cls._get_convert_chain = _get_convert_chain


class Color(metaclass=ColorMeta):
    """Color class object which provides access and manipulation of color spaces."""

    CS_MAP = {}  # type: dict[str, Space]
    DE_MAP = {}  # type: dict[str, DeltaE]
    FIT_MAP = {}  # type: dict[str, Fit]
    CAT_MAP = {}  # type: dict[str, CAT]
    CONTRAST_MAP = {}  # type: dict[str, ColorContrast]
    FILTER_MAP = {}  # type: dict[str, Filter]
    INTERPOLATE_MAP = {}  # type: dict[str, Interpolate]
    PRECISION = util.DEF_PREC
    FIT = util.DEF_FIT
    INTERPOLATE = util.DEF_INTERPOLATE
    DELTA_E = util.DEF_DELTA_E
    HARMONY = util.DEF_HARMONY
    CHROMATIC_ADAPTATION = 'bradford'
    CONTRAST = 'wcag21'

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
        **kwargs: Any
    ) -> None:
        """Initialize."""

        self._space, self._coords = self._parse(color, data, alpha, **kwargs)

    def __len__(self) -> int:
        """Get number of channels."""

        return len(self._space.CHANNELS) + 1

    @overload
    def __getitem__(self, i: str | int) -> float:  # noqa: D105
        ...

    @overload
    def __getitem__(self, i: slice) -> Vector:  # noqa: D105
        ...

    def __getitem__(self, i: str | int | slice) -> float | Vector:
        """Get channels."""

        return self._coords[self._space.get_channel_index(i)] if isinstance(i, str) else self._coords[i]

    @overload
    def __setitem__(self, i: str | int, v: float) -> None:  # noqa: D105
        ...

    @overload
    def __setitem__(self, i: slice, v: Vector) -> None:  # noqa: D105
        ...

    def __setitem__(self, i: str | int | slice, v: float | Vector) -> None:
        """Set channels."""

        space = self._space
        if isinstance(i, slice):
            for index, value in zip(range(len(self._coords))[i], cast(Vector, v)):
                self._coords[index] = alg.clamp(float(value), *space.channels[index].limit)
        else:
            index = space.get_channel_index(i) if isinstance(i, str) else i
            self._coords[index] = alg.clamp(float(cast(float, v)), *space.channels[index].limit)

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
        **kwargs: Any
    ) -> tuple[Space, list[float]]:
        """Parse the color."""

        # Parse a color string or color space name and coordinates
        if isinstance(color, str):

            # Parse a color space name and coordinates
            if data is not None:
                s = color
                space_class = cls.CS_MAP.get(s)
                if not space_class:
                    raise ValueError("'{}' is not a registered color space")
                num_channels = len(space_class.CHANNELS)
                num_data = len(data)
                if num_data < num_channels:
                    data = list(data) + [alg.NaN] * (num_channels - num_data)
                coords = [alg.clamp(float(v), *c.limit) for c, v in zipl(space_class.CHANNELS, data)]
                coords.append(alg.clamp(float(alpha), *space_class.channels[-1].limit))
                obj = space_class, coords

            # Parse a CSS string
            else:
                m = cls._match(color, fullmatch=True)
                if m is None:
                    raise ValueError("'{}' is not a valid color".format(color))
                coords = [alg.clamp(float(v), *c.limit) for c, v in zipl(m[0].CHANNELS, m[1])]
                coords.append(alg.clamp(float(m[2]), *m[0].channels[-1].limit))
                obj = m[0], coords

        # Handle a color instance
        elif isinstance(color, Color):
            space_class = cls.CS_MAP.get(color.space())
            if not space_class:
                raise ValueError("'{}' is not a registered color space")
            obj = space_class, color[:]

        # Handle a color dictionary
        elif isinstance(color, Mapping):
            obj = cls._parse(color['space'], color['coords'], color.get('alpha', 1.0))

        else:
            raise TypeError("'{}' is an unrecognized type".format(type(color)))

        return obj

    @classmethod
    def _match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = False
    ) -> Optional[tuple[Space, Vector, float, int, int]]:
        """
        Match a color in a buffer and return a color object.

        This must return the color space, not the Color object.
        """

        # Attempt color match
        m = parse.parse_color(string, cls.CS_MAP, start, fullmatch)
        if m is not None:
            return m[0], m[1][0], m[1][1], start, m[2]

        # Attempt color space specific match
        for space, space_class in cls.CS_MAP.items():
            m2 = space_class.match(string, start, fullmatch)
            if m2 is not None:
                return space_class, m2[0][0], m2[0][1], start, m2[1]
        return None

    @classmethod
    def match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = False
    ) -> Optional[ColorMatch]:
        """Match color."""

        m = cls._match(string, start, fullmatch)
        if m is not None:
            return ColorMatch(cls(m[0].NAME, m[1], m[2]), m[3], m[4])
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
        plugin: Plugin | Sequence[Plugin],
        *,
        overwrite: bool = False,
        silent: bool = False
    ) -> None:
        """Register the hook."""

        reset_convert_cache = False

        if not isinstance(plugin, Sequence):
            plugin = [plugin]

        mapping = None  # type: Optional[dict[str, Any]]
        for p in plugin:
            if isinstance(p, Space):
                mapping = cls.CS_MAP
                reset_convert_cache = True
            elif isinstance(p, DeltaE):
                mapping = cls.DE_MAP
            elif isinstance(p, CAT):
                mapping = cls.CAT_MAP
            elif isinstance(p, Filter):
                mapping = cls.FILTER_MAP
            elif isinstance(p, ColorContrast):
                mapping = cls.CONTRAST_MAP
            elif isinstance(p, Interpolate):
                mapping = cls.INTERPOLATE_MAP
            elif isinstance(p, Fit):
                mapping = cls.FIT_MAP
                if p.NAME == 'clip':
                    if reset_convert_cache:  # pragma: no cover
                        cls._get_convert_chain.cache_clear()
                    if not silent:
                        raise ValueError("'{}' is a reserved name for gamut mapping/reduction and cannot be overridden")
                    continue  # pragma: no cover
            else:
                if reset_convert_cache:  # pragma: no cover
                    cls._get_convert_chain.cache_clear()
                raise TypeError("Cannot register plugin of type '{}'".format(type(p)))

            name = p.NAME
            value = p

            if name != "*" and name not in mapping or overwrite:
                cast('dict[str, Plugin]', mapping)[name] = value
            elif not silent:
                if reset_convert_cache:  # pragma: no cover
                    cls._get_convert_chain.cache_clear()
                raise ValueError("A plugin with the name of '{}' already exists or is not allowed".format(name))

        if reset_convert_cache:
            cls._get_convert_chain.cache_clear()

    @classmethod
    def deregister(cls, plugin: str | Sequence[str], *, silent: bool = False) -> None:
        """Deregister a plugin by name of specified plugin type."""

        reset_convert_cache = False

        if isinstance(plugin, str):
            plugin = [plugin]

        mapping = None  # type: Optional[dict[str, Any]]
        for p in plugin:
            if p == '*':
                cls.CS_MAP.clear()
                cls.DE_MAP.clear()
                cls.FIT_MAP.clear()
                cls.CAT_MAP.clear()
                cls.CONTRAST_MAP.clear()
                cls.INTERPOLATE_MAP.clear()
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
            elif ptype == 'contrast':
                mapping = cls.CONTRAST_MAP
            elif ptype == 'interpolate':
                mapping = cls.INTERPOLATE_MAP
            elif ptype == "fit":
                mapping = cls.FIT_MAP
                if name == 'clip':
                    if reset_convert_cache:  # pragma: no cover
                        cls._get_convert_chain.cache_clear()
                    if not silent:
                        raise ValueError("'{}' is a reserved name gamut mapping/reduction and cannot be removed")
                    continue  # pragma: no cover
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

    @classmethod
    def random(cls, space: str, *, limits: Optional[Sequence[Optional[Sequence[float]]]] = None) -> Color:
        """Get a random color."""

        # Get the color space and number of channels
        cs = cls.CS_MAP[space]
        num_chan = len(cs.CHANNELS)

        # Initialize constraints if none were provided
        if limits is None:
            limits = []

        # Acquire the minimum and maximum for the channel and get a random value value between
        length = len(limits)
        coords = []
        for i in range(num_chan):
            chan = limits[i] if i < length else None  # type: Any
            if chan is None:
                chan = cs.channels[i]
                a, b = chan.low, chan.high
            else:
                a, b = chan

            coords.append(random.uniform(a, b))

        # Create the color
        return cls(space, coords)

    def to_dict(self) -> Mapping[str, Any]:
        """Return color as a data object."""

        return {'space': self.space(), 'coords': self[:-1], 'alpha': self[-1]}

    def normalize(self) -> Color:
        """Normalize the color."""

        self[:] = self._space.normalize(self[:])
        return self

    def is_nan(self, name: str) -> bool:
        """Check if channel is NaN."""

        return alg.is_nan(self.get(name))

    def _handle_color_input(self, color: ColorInput) -> Color:
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
        **kwargs: Any
    ) -> Color:
        """Create new color object."""

        return type(self)(color, data, alpha, **kwargs)

    def clone(self) -> Color:
        """Clone."""

        return self.new(self.space(), self[:-1], self[-1])

    def convert(self, space: str, *, fit: bool | str = False, in_place: bool = False) -> Color:
        """Convert to color space."""

        if fit:
            method = None if not isinstance(fit, str) else fit
            if not self.in_gamut(space, tolerance=0.0):
                converted = self.convert(space, in_place=in_place)
                return converted.fit(space, method=method)

        if space == self.space():
            return self if in_place else self.clone()

        c, coords = convert.convert(self, space)
        coords.append(self[-1])
        this = self if in_place else self.clone()
        this._space = c
        this._coords = coords

        return this

    def mutate(
        self,
        color: ColorInput,
        data: Optional[VectorLike] = None,
        alpha: float = util.DEF_ALPHA,
        **kwargs: Any
    ) -> Color:
        """Mutate the current color to a new color."""

        self._space, self._coords = self._parse(color, data=data, alpha=alpha, **kwargs)
        return self

    def update(
        self,
        color: ColorInput,
        data: Optional[VectorLike] = None,
        alpha: float = util.DEF_ALPHA,
        **kwargs: Any
    ) -> Color:
        """Update the existing color space with the provided color."""

        space = self.space()
        self._space, self._coords = self._parse(color, data=data, alpha=alpha, **kwargs)
        if self._space.NAME != space:
            self.convert(space, in_place=True)
        return self

    def to_string(self, **kwargs: Any) -> str:
        """To string."""

        return self._space.to_string(self, **kwargs)

    def __repr__(self) -> str:
        """Representation."""

        return 'color({} {} / {})'.format(
            self._space._serialize()[0],
            ' '.join([util.fmt_float(coord, util.DEF_PREC) for coord in self[:-1]]),
            util.fmt_float(self[-1], util.DEF_PREC)
        )

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
        w1: tuple[float, float],
        w2: tuple[float, float],
        xyz: VectorLike,
        *,
        method: Optional[str] = None
    ) -> Vector:
        """Chromatic adaptation."""

        adapter = cls.CAT_MAP.get(method if method is not None else cls.CHROMATIC_ADAPTATION)
        if not adapter:
            raise ValueError("'{}' is not a supported CAT".format(method))

        return adapter.adapt(w1, w2, xyz)

    def clip(self, space: Optional[str] = None) -> Color:
        """Clip the color channels."""

        orig_space = self.space()
        if space is None:
            space = self.space()

        # Convert to desired space
        c = self.convert(space, in_place=True)
        gamut.clip_channels(c)

        # Adjust "this" color
        return c.convert(orig_space, in_place=True)

    def fit(
        self,
        space: Optional[str] = None,
        *,
        method: Optional[str] = None,
        **kwargs: Any
    ) -> Color:
        """Fit the gamut using the provided method."""

        if method is None:
            method = self.FIT

        # Dedicated clip method.
        if method == 'clip':
            return self.clip(space)

        orig_space = self.space()
        if space is None:
            space = self.space()

        # Select appropriate mapping algorithm
        mapping = self.FIT_MAP.get(method)
        if not mapping:
            # Unknown fit method
            raise ValueError("'{}' gamut mapping is not currently supported".format(method))

        # Convert to desired space
        self.convert(space, in_place=True)

        # Call the appropriate gamut mapping algorithm
        mapping.fit(self, **kwargs)

        # Convert back to the original color space
        return self.convert(orig_space, in_place=True)

    def in_gamut(self, space: Optional[str] = None, *, tolerance: float = util.DEF_FIT_TOLERANCE) -> bool:
        """Check if current color is in gamut."""

        if space is None:
            space = self.space()

        # Check if gamut is in the provided space
        c = self.convert(space) if space is not None and space != self.space() else self

        # Check the color space specified for gamut checking.
        # If it proves to be in gamut, we will then test if the current
        # space is constrained properly.
        if c._space.GAMUT_CHECK is not None and not c.convert(c._space.GAMUT_CHECK).in_gamut(tolerance=tolerance):
            return False

        return gamut.verify(c, tolerance)

    def mask(self, channel: str | Sequence[str], *, invert: bool = False, in_place: bool = False) -> Color:
        """Mask color channels."""

        this = self if in_place else self.clone()
        aliases = self._space.CHANNEL_ALIASES
        masks = set(
            [aliases.get(channel, channel)] if isinstance(channel, str) else [aliases.get(c, c) for c in channel]
        )
        for name in self._space.channels:
            if (not invert and name in masks) or (invert and name not in masks):
                this[name] = alg.NaN
        return this

    def mix(
        self,
        color: ColorInput,
        percent: float = util.DEF_MIX,
        *,
        in_place: bool = False,
        **interpolate_args: Any
    ) -> Color:
        """
        Mix colors using interpolation.

        This uses the interpolate method to find the center point between the two colors.
        The basic mixing logic is outlined in the CSS level 5 draft.
        """

        if not self._is_color(color) and not isinstance(color, (str, Mapping)):
            raise TypeError("Unexpected type '{}'".format(type(color)))
        i = self.interpolate([self, color], **interpolate_args)
        # Scale really needs to be between 0 and 1 as mix deals in percentages.
        if i.domain:
            i.domain = interpolate.normalize_domain(i.domain)
        mixed = i(percent)
        return self.mutate(mixed) if in_place else mixed

    @classmethod
    def steps(
        cls,
        colors: Sequence[ColorInput | interpolate.stop | Callable[..., float]],
        *,
        steps: int = 2,
        max_steps: int = 1000,
        max_delta_e: float = 0,
        delta_e: Optional[str] = None,
        **interpolate_args: Any
    ) -> list[Color]:
        """Discrete steps."""

        i = cls.interpolate(colors, **interpolate_args)
        # Scale really needs to be between 0 and 1 or steps will break
        if i.domain:
            i.domain = interpolate.normalize_domain(i.domain)
        return i.steps(steps, max_steps, max_delta_e, delta_e)

    @classmethod
    def interpolate(
        cls,
        colors: Sequence[ColorInput | interpolate.stop | Callable[..., float]],
        *,
        space: Optional[str] = None,
        out_space: Optional[str] = None,
        progress: Optional[Mapping[str, Callable[..., float]] | Callable[..., float]] = None,
        hue: str = util.DEF_HUE_ADJ,
        premultiplied: bool = True,
        extrapolate: bool = False,
        domain: Optional[list[float]] = None,
        method: str = "linear",
        **kwargs: Any
    ) -> Interpolator:
        """
        Return an interpolation function.

        The function will return an interpolation function that accepts a value (which should
        be in the range of [0..1] and will return a color based on that value.

        While we use NaNs to mask off channels when doing the interpolation, we do not allow
        arbitrary specification of NaNs by the user, they must specify channels via `adjust`
        if they which to target specific channels for mixing. Null hues become NaNs before
        mixing occurs.
        """

        return interpolate.interpolator(
            method,
            cls,
            colors=colors,
            space=space,
            out_space=out_space,
            progress=progress,
            hue=hue,
            premultiplied=premultiplied,
            extrapolate=extrapolate,
            domain=domain,
            **kwargs
        )

    def filter(  # noqa: A003
        self,
        name: str,
        amount: Optional[float] = None,
        *,
        space: Optional[str] = None,
        in_place: bool = False,
        **kwargs: Any
    ) -> Color:
        """Filter."""

        return filters.filters(self, name, amount, space, in_place, **kwargs)

    def harmony(
        self,
        name: str,
        *,
        space: Optional[str] = None
    ) -> list[Color]:
        """Acquire the specified color harmonies."""

        return harmonies.harmonize(self, name, space)

    def compose(
        self,
        backdrop: ColorInput | Sequence[ColorInput],
        *,
        blend: str | bool = True,
        operator: str | bool = True,
        space: Optional[str] = None,
        out_space: Optional[str] = None,
        in_place: bool = False
    ) -> Color:
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

        delta = self.DE_MAP.get(method)
        if not delta:
            raise ValueError("'{}' is not currently a supported distancing algorithm.".format(method))
        return delta.distance(self, color, **kwargs)

    def distance(self, color: ColorInput, *, space: str = "lab") -> float:
        """Delta."""

        return distance.distance_euclidean(self, self._handle_color_input(color), space=space)

    def closest(
        self,
        colors: Sequence[ColorInput],
        *,
        method: Optional[str] = None,
        **kwargs: Any
    ) -> Color:
        """Find the closest color to the current base color."""

        return distance.closest(self, colors, method=method, **kwargs)

    def luminance(self) -> float:
        """Get color's luminance."""

        return self.convert("xyz-d65")['y']

    def contrast(self, color: ColorInput, method: Optional[str] = None) -> float:
        """Compare the contrast ratio of this color and the provided color."""

        color = self._handle_color_input(color)
        return contrast.contrast(method, self, color)

    @overload
    def get(self, name: str) -> float:  # noqa: D105
        ...

    @overload
    def get(self, name: list[str] | tuple[str, ...]) -> list[float]:  # noqa: D105
        ...

    def get(self, name: str | list[str] | tuple[str, ...]) -> float | list[float]:
        """Get channel."""

        # Handle single channel
        if isinstance(name, str):
            # Handle space.channel
            if '.' in name:
                space, channel = name.split('.', 1)
                return self.convert(space)[channel]
            return self[name]

        # Handle list of channels
        else:
            original_space = current_space = self.space()
            obj = self
            values = []

            for n in name:
                # Handle space.channel
                space, channel = n.split('.', 1) if '.' in n else (original_space, n)
                if space != current_space:
                    obj = self if space == original_space else self.convert(space)
                    current_space = space
                values.append(obj[channel])
            return values

    def set(  # noqa: A003
        self,
        name: str | dict[str, float | Callable[..., float]],
        value: Optional[float | Callable[..., float]] = None
    ) -> Color:
        """Set channel."""

        # Set all the channels in a dictionary.
        # Sort by name to reduce how many times we convert
        # when dealing with different color spaces.
        if value is None:
            if isinstance(name, str):
                raise ValueError("Missing the positional 'value' argument for channel '{}'".format(name))

            original_space = current_space = self.space()
            obj = self.clone()

            for k, v in name.items():

                # Handle space.channel
                space, channel = k.split('.', 1) if '.' in k else (original_space, k)
                if space != current_space:
                    obj.convert(space, in_place=True)
                    current_space = space
                obj[channel] = v(obj[channel]) if callable(v) else v

            # Update the original color
            self.update(obj)

        # Set a single channel value
        else:
            if isinstance(name, dict):
                raise ValueError("A dict of channels and values cannot be used with the positional 'value' parameter")

            # Handle space.channel
            if '.' in name:
                space, channel = name.split('.', 1)
                obj = self.convert(space)
                obj[channel] = value(obj[channel]) if callable(value) else value
                return self.update(obj)

            # Handle a function that modifies the value or a direct value
            self[name] = value(self[name]) if callable(value) else value

        return self


Color.register(
    [
        # Spaces
        XYZD65(),
        XYZD50(),
        sRGB(),
        sRGBLinear(),
        DisplayP3(),
        DisplayP3Linear(),
        Oklab(),
        OkLCh(),
        Lab(),
        LCh(),
        LabD65(),
        LChD65(),
        HSV(),
        HSL(),
        HWB(),
        Rec2020(),
        Rec2020Linear(),
        A98RGB(),
        A98RGBLinear(),
        ProPhotoRGB(),
        ProPhotoRGBLinear(),

        # CAT
        Bradford(),

        # Delta E
        DE76(),
        DE94(),
        DECMC(),
        DE2000(),
        DEHyAB(),
        DEOK(),

        # Fit
        LChChroma(),
        OkLChChroma(),

        # Filters
        Sepia(),
        Brightness(),
        Contrast(),
        Saturate(),
        Opacity(),
        HueRotate(),
        Grayscale(),
        Invert(),
        Protan(),
        Deutan(),
        Tritan(),

        # Contrast
        WCAG21Contrast(),

        # Interpolation
        Linear(),
        BSpline(),
        NaturalBSpline(),
        Monotone()
    ]
)
