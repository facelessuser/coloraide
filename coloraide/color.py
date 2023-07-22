"""Colors."""
from __future__ import annotations
import abc
import functools
import random
import math
from . import cat
from . import distance
from . import convert
from . import gamut
from . import compositing
from . import interpolate
from . import filters
from . import contrast
from . import harmonies
from . import average
from . import temperature
from . import util
from . import algebra as alg
from itertools import zip_longest as zipl
from .css import parse
from .types import VectorLike, Vector, ColorInput
from .spaces import Space, RGBish
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
from .interpolate.linear import Linear
from .interpolate.continuous import Continuous
from .interpolate.bspline import BSpline
from .interpolate.bspline_natural import NaturalBSpline
from .interpolate.monotone import Monotone
from .temperature import CCT
from .temperature.ohno_2013 import Ohno2013
from .temperature.robertson_1968 import Robertson1968
from .types import Plugin
from typing import overload, Sequence, Iterable, Any, Callable, Mapping

SUPPORTED_CHROMATICITY_SPACES = set(('xyz', 'uv-1960', 'uv-1976', 'xy-1931'))


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
            cls.CCT_MAP = cls.CCT_MAP.copy()  # type: dict[str, CCT]

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
    CCT_MAP = {}  # type: dict[str, CCT]
    PRECISION = util.DEF_PREC
    FIT = util.DEF_FIT
    INTERPOLATE = util.DEF_INTERPOLATE
    DELTA_E = util.DEF_DELTA_E
    HARMONY = util.DEF_HARMONY
    AVERAGE = util.DEF_AVERAGE
    CHROMATIC_ADAPTATION = util.DEF_CHROMATIC_ADAPTATION
    CONTRAST = util.DEF_CONTRAST
    CCT = util.DEF_CCT

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
        data: VectorLike | None = None,
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
            for index, value in zip(range(len(self._coords))[i], v):  # type: ignore[arg-type]
                self._coords[index] = alg.clamp(float(value), *space.channels[index].limit)
        else:
            index = space.get_channel_index(i) if isinstance(i, str) else i
            self._coords[index] = alg.clamp(float(v), *space.channels[index].limit)  # type: ignore[arg-type]

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
        data: VectorLike | None = None,
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
                    raise ValueError("'{}' is not a registered color space".format(s))
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
                raise ValueError("'{}' is not a registered color space".format(color.space()))
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
    ) -> tuple[Space, Vector, float, int, int] | None:
        """
        Match a color in a buffer and return a color object.

        This must return the color space, not the Color object.
        """

        # Attempt color match
        if string[start:start + 6].lower() == 'color(':
            for space_class in cls.CS_MAP.values():
                if not space_class.COLOR_FORMAT:  # pragma: no cover
                    continue
                m = parse.parse_css(space_class, string, start, fullmatch, True)
                if m is not None:
                    return space_class, m[0][0], m[0][1], start, m[1]

        # Attempt color space specific match
        for _, space_class in cls.CS_MAP.items():
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
    ) -> ColorMatch | None:
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
        mapping = None  # type: Any
        p = None  # type: Any
        for i in [plugin] if not isinstance(plugin, Sequence) else plugin:
            if isinstance(i, Space):
                mapping = cls.CS_MAP
                reset_convert_cache = True
                p = i
            elif isinstance(i, DeltaE):
                mapping = cls.DE_MAP
                p = i
            elif isinstance(i, CAT):
                mapping = cls.CAT_MAP
                p = i
            elif isinstance(i, Filter):
                mapping = cls.FILTER_MAP
                p = i
            elif isinstance(i, ColorContrast):
                mapping = cls.CONTRAST_MAP
                p = i
            elif isinstance(i, Interpolate):
                mapping = cls.INTERPOLATE_MAP
                p = i
            elif isinstance(i, CCT):
                mapping = cls.CCT_MAP
                p = i
            elif isinstance(i, Fit):
                mapping = cls.FIT_MAP
                p = i
                if p.NAME == 'clip':
                    if reset_convert_cache:  # pragma: no cover
                        cls._get_convert_chain.cache_clear()
                    if not silent:
                        raise ValueError("'{}' is a reserved name for gamut mapping/reduction and cannot be overridden")
                    continue  # pragma: no cover
            else:
                if reset_convert_cache:  # pragma: no cover
                    cls._get_convert_chain.cache_clear()
                raise TypeError("Cannot register plugin of type '{}'".format(type(i)))

            if p.NAME != "*" and p.NAME not in mapping or overwrite:
                mapping[p.NAME] = p
            elif not silent:
                if reset_convert_cache:  # pragma: no cover
                    cls._get_convert_chain.cache_clear()
                raise ValueError("A plugin of name '{}' already exists or is not allowed".format(p.NAME))

        if reset_convert_cache:
            cls._get_convert_chain.cache_clear()

    @classmethod
    def deregister(cls, plugin: str | Sequence[str], *, silent: bool = False) -> None:
        """Deregister a plugin by name of specified plugin type."""

        reset_convert_cache = False

        if isinstance(plugin, str):
            plugin = [plugin]

        mapping = None  # type: dict[str, Any] | None
        for p in plugin:
            if p == '*':
                cls.CS_MAP.clear()
                cls.DE_MAP.clear()
                cls.CAT_MAP.clear()
                cls.FILTER_MAP.clear()
                cls.CONTRAST_MAP.clear()
                cls.INTERPOLATE_MAP.clear()
                cls.CCT_MAP.clear()
                cls.FIT_MAP.clear()
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
            elif ptype == 'cct':
                mapping = cls.CCT_MAP
            elif ptype == "fit":
                mapping = cls.FIT_MAP
                if name == 'clip':
                    if reset_convert_cache:  # pragma: no cover
                        cls._get_convert_chain.cache_clear()
                    if not silent:
                        raise ValueError(
                            "'{}' is a reserved name gamut mapping/reduction and cannot be removed".format(name)
                        )
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
    def random(cls, space: str, *, limits: Sequence[Sequence[float] | None] | None = None) -> Color:
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
        obj = cls(space, coords)
        if hasattr(obj._space, 'hue_index'):
            obj.normalize()
        return obj

    @classmethod
    def blackbody(
        cls,
        space: str,
        temp: float,
        duv: float = 0.0,
        *,
        scale: bool = True,
        scale_space: str | None = None,
        method: str | None = None,
        **kwargs: Any
    ) -> Color:
        """
        Get a color along the black body curve.

        Colors are specified by temperature in Kelvin. Depending on the algorithm, the practical
        range may differ.

        Colors are returned and normalized to be within the specified RGB space (preferably linear).
        The returned color, after normalization, is an approximation and may not exactly match the
        temperature. If `space` is set to `None` the color will not be normalized and may not be in
        the visible spectrum, but it should correlate with the specified temperature assuming it is
        not too far from the locus.
        """

        cct = temperature.cct(method, cls)
        color = cct.from_cct(cls, space, temp, duv, scale, scale_space, **kwargs)
        return color

    def cct(self, *, method: str | None = None, **kwargs: Any) -> Vector:
        """Get color temperature."""

        cct = temperature.cct(method, self)
        return cct.to_cct(self, **kwargs)

    def to_dict(self, *, nans: bool = True) -> Mapping[str, Any]:
        """Return color as a data object."""

        return {'space': self.space(), 'coords': self.coords(nans=nans), 'alpha': self.alpha(nans=nans)}

    def normalize(self, *, nans: bool = True) -> Color:
        """Normalize the color."""

        self[:-1] = self.coords(nans=False)
        if nans and hasattr(self._space, 'hue_index') and self.is_achromatic():
            i = self._space.hue_index()
            self[i] = alg.NaN
        self[-1] = alg.no_nan(self[-1])
        return self

    def is_nan(self, name: str) -> bool:  # pragma: no cover
        """Check if channel is NaN."""

        return math.isnan(self.get(name))

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
        data: VectorLike | None = None,
        alpha: float = util.DEF_ALPHA,
        **kwargs: Any
    ) -> Color:
        """Create new color object."""

        return type(self)(color, data, alpha, **kwargs)

    def clone(self) -> Color:
        """Clone."""

        return self.new(self.space(), self[:-1], self[-1])

    def convert(
        self,
        space: str,
        *,
        fit: bool | str = False,
        in_place: bool = False,
        norm: bool = True
    ) -> Color:
        """Convert to color space."""

        # Convert the color and then fit it.
        if fit:
            method = None if not isinstance(fit, str) else fit
            if not self.in_gamut(space, tolerance=0.0):
                converted = self.convert(space, in_place=in_place, norm=norm)
                return converted.fit(space, method=method)

        # Nothing to do, just return the color with no alterations.
        if space == self.space():
            return self if in_place else self.clone()

        # Actually convert the color
        c, coords = convert.convert(self, space)
        this = self if in_place else self.clone()
        this._space = c
        this._coords[:-1] = coords

        # Normalize achromatic colors, but skip if we internally don't need this.
        if norm and hasattr(this._space, 'hue_index') and this.is_achromatic():
            this[this._space.hue_index()] = alg.NaN

        return this

    def is_achromatic(self) -> bool:
        """Test if color is achromatic."""

        value = self._space.is_achromatic(self.coords(nans=False))
        if value is None:
            xyz = self.convert('xyz-d65')
            return bool(xyz._space.is_achromatic(xyz[:-1]))
        return value

    def mutate(
        self,
        color: ColorInput,
        data: VectorLike | None = None,
        alpha: float = util.DEF_ALPHA,
        **kwargs: Any
    ) -> Color:
        """Mutate the current color to a new color."""

        self._space, self._coords = self._parse(color, data=data, alpha=alpha, **kwargs)
        return self

    def update(
        self,
        color: ColorInput,
        data: VectorLike | None = None,
        alpha: float = util.DEF_ALPHA,
        *,
        norm: bool = True,
        **kwargs: Any
    ) -> Color:
        """Update the existing color space with the provided color."""

        space = self.space()
        self._space, self._coords = self._parse(color, data=data, alpha=alpha, **kwargs)
        if self._space.NAME != space:
            self.convert(space, in_place=True, norm=norm)
        return self

    def _hotswap(self, color: Color) -> Color:
        """
        Hot swap a color object.

        We expect it to be a color object, no special parsing, we just want to go fast.
        """

        self._space, self._coords = self.CS_MAP[color.space()], color[:]
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

    def white(self, cspace: str = 'xyz') -> Vector:
        """Get the white point."""

        value = self.convert_chromaticity('xy-1931', cspace, self._space.WHITE)
        return value if cspace == 'xyz' else value[:-1]

    def uv(self, mode: str = '1976', *, white: VectorLike | None = None) -> Vector:
        """Convert to `xy`."""

        return self.split_chromaticity('uv-' + mode)[:-1]

    def xy(self, *, white: VectorLike | None = None) -> Vector:
        """Convert to `xy`."""

        return self.split_chromaticity('xy-1931')[:-1]

    def split_chromaticity(
        self,
        cspace: str = 'uv-1976',
        *,
        white: VectorLike | None = None
    ) -> Vector:
        """
        Split a color into chromaticity and luminance coordinates.

        Colors are split under the XYZ color space using the current color's white point.
        If results are desired relative to a different white point, one can be provided.
        """

        if white is None:
            white = self._space.WHITE

        # Convert to XYZ D65 as it is a color space that is always required.
        # Chromatically adapt it to the XYZ color space with the current color's white point.
        xyz = self.convert('xyz-d65')
        coords = self.chromatic_adaptation(
            xyz._space.WHITE,
            white,
            xyz.coords(nans=False)
        )

        # XYZ is not a chromaticity space
        if cspace == 'xyz':
            raise ValueError('XYZ is not a luminant-chromaticity color space.')

        # Convert to the the requested uv color space if required.
        return (
            self.convert_chromaticity('xyz', cspace, coords, white=white) if cspace != 'xy_1931' else coords
        )

    @classmethod
    def chromaticity(
        cls,
        space: str,
        coords: VectorLike,
        cspace: str = 'uv-1976',
        *,
        scale: bool = False,
        scale_space: str | None = None,
        white: VectorLike | None = None
    ) -> Color:
        """
        Create a color from chromaticity coordinates.

        A luminance of 1 will be assumed unless luminance is included with the coordinates.
        The relative white point of the chromaticity coordinates will be assumed as the
        targeted color space unless one is provided via `white`.

        Lastly, colors can be scaled/normalized within a linear RGB space to normalize
        luminance and provide a nice viewable color. This is useful when the luminance is
        not accurate (such as when luminance is assumed 1). Colors that are out of the linear
        RGB space's gamut will only be rough approximations of the color due to gamut
        limitations. Default linear RGB space is linear sRGB.
        """

        if scale_space is None:
            scale_space = 'srgb-linear'

        # Use the white point of the target color space unless a white point is given.
        if white is None:
            white = cls.CS_MAP[space].WHITE

        # XYZ is not a chromaticity space
        if cspace == 'xyz':
            raise ValueError('XYZ is not a luminant-chromaticity color space.')

        coords = cls.convert_chromaticity(cspace, 'xyz', coords, white=white)

        # Apply chromatic adaptation to match XYZ D65 white point
        color = cls(
            'xyz-d65',
            cls.chromatic_adaptation(white, cls.CS_MAP['xyz-d65'].WHITE, coords)
        )

        # Normalize in the given RGB color space (ideally linear).
        if scale and isinstance(cls.CS_MAP[scale_space], RGBish):
            color.convert(scale_space, in_place=True)
            color[:-1] = util.rgb_scale(color.coords())

        # Convert to targeted color space
        if space != color.space():
            color.convert(space, in_place=True)

        return color

    @classmethod
    def convert_chromaticity(
        cls, cspace1: str,
        cspace2: str,
        coords: VectorLike,
        *,
        white: VectorLike | None = None
    ) -> Vector:
        """
        Convert to or from chromaticity coordinates or between other chromaticity coordinates.

        When converting to or from chromaticity coordinates, the coordinates must be in the XYZ space.
        A white point can be provided and only serves to align colors like black on the achromatic axis;
        otherwise, black will be returned as [0, 0] for the two respective chromaticity points.
        """

        # Check that we know the requested spaces
        if cspace1 not in SUPPORTED_CHROMATICITY_SPACES:
            raise ValueError("Unexpected chromaticity space '{}'".format(cspace1))
        if cspace2 not in SUPPORTED_CHROMATICITY_SPACES:
            raise ValueError("Unexpected chromaticity space '{}'".format(cspace2))

        # Return if there is nothing to convert
        l = len(coords)
        if (cspace1 == 'xyz' and l != 3) or l not in (2, 3):
            raise ValueError('Unexpected number of coordinates ({}) for {}'.format(l, cspace1))

        # Return if already in desired form
        if cspace1 == cspace2:
            return list(coords) + [1] if l == 2 else list(coords)

        # If starting space is XYZ, then convert to xy
        if cspace1 == 'xyz':
            coords = util.xyz_to_xyY(coords, [0.0] * 2 if white is None else white)
            cspace1 = 'xy-1931'

            # If the end space is xy, we have nothing else to do
            if cspace2 == cspace1:
                return coords

        # If we have no luminance, assume 1
        pair, Y = (coords[:-1], coords[-1]) if l == 3 else (coords, 1.0)

        # If we are targeting XYZ, force conversion to xy first.
        target = cspace2
        if cspace2 == 'xyz':
            cspace2 = 'xy-1931'

        # Perform conversion
        if cspace1 == 'xy-1931' and cspace2 != 'xy-1931':
            pair = util.xy_to_uv_1960(pair) if cspace2 == 'uv-1960' else util.xy_to_uv(pair)
        elif cspace1 == 'uv-1960':
            pair = util.uv_1960_to_xy(pair) if cspace2 == 'xy-1931' else util.xy_to_uv(util.uv_1960_to_xy(pair))
        elif cspace1 == 'uv-1976':
            pair = util.uv_to_xy(pair) if cspace2 == 'xy-1931' else util.xy_to_uv_1960(util.uv_to_xy(pair))

        # Special case to convert to XYZ from xy
        if target == 'xyz':
            return util.xy_to_xyz(pair, Y)

        return list(pair) + [Y]

    @classmethod
    def chromatic_adaptation(
        cls,
        w1: VectorLike,
        w2: VectorLike,
        xyz: VectorLike,
        *,
        method: str | None = None
    ) -> Vector:
        """Chromatic adaptation."""

        adapter = cls.CAT_MAP.get(method if method is not None else cls.CHROMATIC_ADAPTATION)
        if not adapter:
            raise ValueError("'{}' is not a supported CAT".format(method))

        return adapter.adapt(tuple(w1), tuple(w2), xyz)  # type: ignore[arg-type]

    def clip(self, space: str | None = None) -> Color:
        """Clip the color channels."""

        orig_space = self.space()
        if space is None:
            space = self.space()

        # Convert to desired space
        c = self.convert(space, in_place=True, norm=False)
        gamut.clip_channels(c)

        # Adjust "this" color
        return c.convert(orig_space, in_place=True)

    def fit(
        self,
        space: str | None = None,
        *,
        method: str | None = None,
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
        self.convert(space, in_place=True, norm=False)

        # If within gamut, just normalize hue range by calling clip.
        if self.in_gamut(tolerance=0):
            gamut.clip_channels(self)

        # Perform gamut mapping.
        else:
            mapping.fit(self, **kwargs)

        # Convert back to the original color space
        return self.convert(orig_space, in_place=True)

    def in_gamut(self, space: str | None = None, *, tolerance: float = util.DEF_FIT_TOLERANCE) -> bool:
        """Check if current color is in gamut."""

        if space is None:
            space = self.space()

        # Check if gamut is in the provided space
        c = self.convert(space, norm=False) if space is not None and space != self.space() else self

        # Check the color space specified for gamut checking.
        # If it proves to be in gamut, we will then test if the current
        # space is constrained properly.
        if (
            c._space.GAMUT_CHECK is not None and
            not c.convert(c._space.GAMUT_CHECK, norm=False).in_gamut(tolerance=tolerance)
        ):
            return False

        return gamut.verify(c, tolerance)

    def in_pointer_gamut(self, *, tolerance: float = util.DEF_FIT_TOLERANCE) -> bool:
        """Check if in pointer gamut."""

        return gamut.pointer.in_pointer_gamut(self, tolerance)

    def fit_pointer_gamut(self) -> Color:
        """Check if in pointer gamut."""

        return gamut.pointer.fit_pointer_gamut(self)

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
        return self._hotswap(mixed) if in_place else mixed

    @classmethod
    def steps(
        cls,
        colors: Sequence[ColorInput | interpolate.stop | Callable[..., float]],
        *,
        steps: int = 2,
        max_steps: int = 1000,
        max_delta_e: float = 0,
        delta_e: str | None = None,
        **interpolate_args: Any
    ) -> list[Color]:
        """Discrete steps."""

        i = cls.interpolate(colors, **interpolate_args)
        # Scale really needs to be between 0 and 1 or steps will break
        if i.domain:
            i.domain = interpolate.normalize_domain(i.domain)
        return i.steps(steps, max_steps, max_delta_e, delta_e)

    @classmethod
    def discrete(
        cls,
        colors: Sequence[ColorInput | interpolate.stop | Callable[..., float]],
        *,
        space: str | None = None,
        out_space: str | None = None,
        steps: int | None = None,
        domain: list[float] | None = None,
        **interpolate_steps_args: Any
    ) -> Interpolator:
        """Create a discrete interpolation."""

        # If no steps were provided, use the number of colors provided
        if steps is None:
            steps = sum((not callable(c) or not isinstance(c, interpolate.stop)) for c in colors)

        # Generate the discrete color steps
        colors = cls.steps(colors, space=space, steps=steps, **interpolate_steps_args)

        # Create an interpolation with discrete ranges
        total = len(colors)
        discrete = []
        for r in range(1, total):
            step1 = colors[r - 1]
            step2 = colors[r]
            stp = r / total
            discrete.extend([interpolate.stop(step1, stp), interpolate.stop(step2, stp)])

        return cls.interpolate(discrete, space=space, out_space=out_space, domain=domain)

    @classmethod
    def interpolate(
        cls,
        colors: Sequence[ColorInput | interpolate.stop | Callable[..., float]],
        *,
        space: str | None = None,
        out_space: str | None = None,
        progress: Mapping[str, Callable[..., float]] | Callable[..., float] | None = None,
        hue: str = util.DEF_HUE_ADJ,
        premultiplied: bool = True,
        extrapolate: bool = False,
        domain: list[float] | None = None,
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

    @classmethod
    def average(
        cls,
        colors: Iterable[ColorInput],
        *,
        space: str | None = None,
        out_space: str | None = None,
        premultiplied: bool = True,
        **kwargs: Any
    ) -> Color:
        """Average the colors."""

        if space is None:
            space = cls.AVERAGE

        if out_space is None:
            out_space = space

        return average.average(cls, colors, space, premultiplied).convert(out_space, in_place=True)

    def filter(  # noqa: A003
        self,
        name: str,
        amount: float | None = None,
        *,
        space: str | None = None,
        out_space: str | None = None,
        in_place: bool = False,
        **kwargs: Any
    ) -> Color:
        """Filter."""

        return filters.filters(self, name, amount, space, out_space, in_place, **kwargs)

    def harmony(
        self,
        name: str,
        *,
        space: str | None = None,
        out_space: str | None = None
    ) -> list[Color]:
        """Acquire the specified color harmonies."""

        if space is None:
            space = self.HARMONY

        if out_space is None:
            out_space = space

        return [c.convert(out_space, in_place=True) for c in harmonies.harmonize(self, name, space)]

    def compose(
        self,
        backdrop: ColorInput | Sequence[ColorInput],
        *,
        blend: str | bool = True,
        operator: str | bool = True,
        space: str | None = None,
        out_space: str | None = None,
        in_place: bool = False
    ) -> Color:
        """Blend colors using the specified blend mode."""

        if not isinstance(backdrop, str) and isinstance(backdrop, Sequence):
            bcolor = [self._handle_color_input(c) for c in backdrop]
        else:
            bcolor = [self._handle_color_input(backdrop)]

        color = compositing.compose(self, bcolor, blend, operator, space, out_space)
        return self._hotswap(color) if in_place else color

    def delta_e(
        self,
        color: ColorInput,
        *,
        method: str | None = None,
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
        method: str | None = None,
        **kwargs: Any
    ) -> Color:
        """Find the closest color to the current base color."""

        return distance.closest(self, colors, method=method, **kwargs)

    def luminance(self, *, white: VectorLike | None = cat.WHITES['2deg']['D65']) -> float:
        """Get color's luminance."""

        if white is None:
            white = self._space.WHITE

        # Convert to XYZ D65 as it is a color space that is always required.
        # Chromatically adapt it to the XYZ color space with the current color's white point.
        xyz = self.convert('xyz-d65')
        coords = self.chromatic_adaptation(
            xyz._space.WHITE,
            white,
            xyz.coords(nans=False)
        )

        return coords[1]

    def contrast(self, color: ColorInput, method: str | None = None) -> float:
        """Compare the contrast ratio of this color and the provided color."""

        color = self._handle_color_input(color)
        return contrast.contrast(method, self, color)

    @overload
    def get(self, name: str, *, nans: bool = True) -> float:  # noqa: D105
        ...

    @overload
    def get(self, name: list[str] | tuple[str, ...], *, nans: bool = True) -> list[float]:  # noqa: D105
        ...

    def get(self, name: str | list[str] | tuple[str, ...], *, nans: bool = True) -> float | list[float]:
        """Get channel."""

        # Handle single channel
        if isinstance(name, str):
            # Handle space.channel
            if '.' in name:
                space, channel = name.split('.', 1)
                if nans:
                    return self.convert(space)[channel]
                else:
                    obj = self.convert(space, norm=nans)
                    i = obj._space.get_channel_index(channel)
                    return obj._space.resolve_channel(i, obj._coords)
            elif nans:
                return self[name]
            else:
                i = self._space.get_channel_index(name)
                return self._space.resolve_channel(i, self._coords)

        # Handle list of channels
        else:
            original_space = current_space = self.space()
            obj = self
            values = []

            for n in name:
                # Handle space.channel
                space, channel = n.split('.', 1) if '.' in n else (original_space, n)
                if space != current_space:
                    obj = self if space == original_space else self.convert(space, norm=nans)
                    current_space = space
                if nans:
                    values.append(obj[channel])
                else:
                    i = obj._space.get_channel_index(channel)
                    values.append(obj._space.resolve_channel(i, obj._coords))
            return values

    def set(  # noqa: A003
        self,
        name: str | dict[str, float | Callable[..., float]],
        value: float | Callable[..., float] | None = None,
        *,
        nans: bool = True
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
                    obj.convert(space, in_place=True, norm=nans)
                    current_space = space
                if not callable(v):
                    obj[channel] = v
                else:
                    i = obj._space.get_channel_index(channel)
                    obj[channel] = v(obj[i] if nans else obj._space.resolve_channel(i, obj._coords))

            # Update the original color
            self.update(obj)

        # Set a single channel value
        else:
            if isinstance(name, dict):
                raise ValueError("A dict of channels and values cannot be used with the positional 'value' parameter")

            # Handle space.channel
            if '.' in name:
                space, channel = name.split('.', 1)
                obj = self.convert(space, norm=nans)
                if not callable(value):
                    obj[channel] = value
                else:
                    i = obj._space.get_channel_index(channel)
                    obj[channel] = value(obj[i] if nans else obj._space.resolve_channel(i, obj._coords))
                return self.update(obj)

            # Handle a function that modifies the value or a direct value
            if not callable(value):
                self[name] = value
            else:
                i = self._space.get_channel_index(name)
                self[name] = value(self[i] if nans else self._space.resolve_channel(i, self._coords))

        return self

    def coords(self, *, nans: bool = True) -> Vector:
        """Get the color channels and optionally remove undefined values."""

        if nans:
            return self[:-1]
        else:
            return [self._space.resolve_channel(index, self._coords) for index in range(len(self._coords) - 1)]

    def alpha(self, *, nans: bool = True) -> float:
        """Get the alpha channel."""

        if nans:
            return self[-1]
        else:
            return self._space.resolve_channel(-1, self._coords)


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
        Continuous(),
        BSpline(),
        NaturalBSpline(),
        Monotone(),

        # CCT
        Robertson1968(),
        Ohno2013()
    ]
)
