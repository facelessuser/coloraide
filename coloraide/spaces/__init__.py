"""Color base."""
from abc import ABCMeta, abstractmethod
from .. import util
from ..util import Vector, MutableVector
from .. import parse
from typing import Tuple, Dict, Pattern, Optional, Union, Sequence, Any, List, cast, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

# Technically, this form could handle any number of channels as long as any extra
# are thrown away. Currently, each space only allows exact, expected channels.
# In the future, we could allow colors to accept more and throw away extras
# like the CSS specification requires.
RE_DEFAULT_MATCH = r"""(?xi)
color\(\s*
(?:({{color_space}})\s+)?
((?:{percent}|{float})(?:{space}(?:{percent}|{float})){{{{,{{channels:d}}}}}}(?:{slash}(?:{percent}|{float}))?)
\s*\)
""".format(
    **parse.COLOR_PARTS
)


# From CIE 2004 Colorimetry T.3 and T.8
# B from https://en.wikipedia.org/wiki/Standard_illuminant#White_point
WHITES = {
    "A": (0.44758, 0.40745),
    "B": (0.34842, 0.35161),
    "C": (0.31006, 0.31616),
    "D50": (0.34570, 0.35850),  # Use 4 digits like everyone
    "D55": (0.33243, 0.34744),
    "D65": (0.31270, 0.32900),  # Use 4 digits like everyone
    "D75": (0.29903, 0.31488),
    "E": (1 / 3, 1 / 3),
    "F2": (0.37210, 0.37510),
    "F7": (0.31290, 0.32920),
    "F11": (0.38050, 0.37690)
}

FLG_ANGLE = 0x1
FLG_PERCENT = 0x2
FLG_OPT_PERCENT = 0x4


class Bounds:
    """Immutable."""

    __slots__ = ('lower', 'upper', 'flags')

    def __init__(self, lower: float, upper: float, flags: int = 0) -> None:
        """Initialize."""

        self.lower = lower
        self.upper = upper
        self.flags = flags

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutability."""

        if not hasattr(self, name) and name in self.__slots__:
            super().__setattr__(name, value)
            return

        raise AttributeError("'{}' is immutable".format(self.__class__.__name__))  # pragma: no cover

    def __repr__(self) -> str:  # pragma: no cover
        """Representation."""

        return "{}({})".format(
            self.__class__.__name__, ', '.join(["{}={!r}".format(k, getattr(self, k)) for k in self.__slots__])
        )

    __str__ = __repr__


class GamutBound(Bounds):
    """Bounded gamut value."""


class GamutUnbound(Bounds):
    """Unbounded gamut value."""


class Cylindrical:
    """Cylindrical space."""

    @classmethod
    def hue_name(cls) -> str:
        """Hue channel name."""

        return "h"

    @classmethod
    def hue_index(cls) -> int:  # pragma: no cover
        """Get hue index."""

        return cast(Type['Space'], cls).CHANNEL_NAMES.index(cls.hue_name())


class Labish:
    """Lab-ish color spaces."""

    @classmethod
    def labish_names(cls) -> Tuple[str, ...]:
        """Return Lab-ish names in the order L a b."""

        return cast(Type['Space'], cls).CHANNEL_NAMES

    @classmethod
    def labish_indexes(cls) -> List[int]:  # pragma: no cover
        """Return the index of the Lab-ish channels."""

        names = cls.labish_names()
        return [cast(Type['Space'], cls).CHANNEL_NAMES.index(name) for name in names]


class Lchish(Cylindrical):
    """Lch-ish color spaces."""

    @classmethod
    def lchish_names(cls) -> Tuple[str, ...]:  # pragma: no cover
        """Return Lch-ish names in the order L c h."""

        return cast(Type['Space'], cls).CHANNEL_NAMES

    @classmethod
    def lchish_indexes(cls) -> List[int]:  # pragma: no cover
        """Return the index of the Lab-ish channels."""

        names = cls.lchish_names()
        return [cast(Type['Space'], cls).CHANNEL_NAMES.index(name) for name in names]


class BaseSpace(ABCMeta):
    """Ensure on subclass that the subclass has new instances of mappings."""

    def __init__(cls, name: str, bases: Tuple[object, ...], clsdict: Dict[str, Any]) -> None:
        """Copy mappings on subclass."""

        if len(cls.mro()) > 2:
            cls.CHANNEL_ALIASES = cls.CHANNEL_ALIASES.copy()  # type: Dict[str, str]


class Space(
    metaclass=BaseSpace
):
    """Base color space object."""

    BASE = ""  # type: str
    # Color space name
    NAME = ""
    # Serialized name
    SERIALIZE = tuple()  # type: Tuple[str, ...]
    # Channel names
    CHANNEL_NAMES = tuple()  # type: Tuple[str, ...]
    # Channel aliases
    CHANNEL_ALIASES = {}  # type: Dict[str, str]
    # For matching the default form of `color(space coords+ / alpha)`.
    # Classes should define this if they want to use the default match.
    DEFAULT_MATCH = None  # type: Optional[Pattern[str]]
    # Match pattern variable for classes to override so we can also
    # maintain the default and other alternatives.
    MATCH = None  # type: Optional[Pattern[str]]
    # Should this color also be checked in a different color space? Only when set to a string (specifying a color space)
    # will the default gamut checking also check the specified space as well as the current.
    #
    # Gamut checking:
    #   The specified color space will be checked first followed by the original. Assuming the parent color space fits,
    #   the original should fit as well, but there are some cases when a parent color space that is slightly out of
    #   gamut, when evaluated with a threshold, may appear to be in gamut enough, but when checking the original color
    #   space, the values can be greatly out of specification (looking at you HSL).
    GAMUT_CHECK = None  # type: Optional[str]
    # When set to `True`, this denotes that the color space has the ability to represent out of gamut in colors in an
    # extended range. When interpolation is done, if colors are interpolated in a smaller gamut than the colors being
    # interpolated, the colors will usually be gamut mapped, but if the interpolation space happens to support extended
    # ranges, then the colors will not be gamut mapped even if their gamut is larger than the target interpolation
    # space.
    EXTENDED_RANGE = False
    # Bounds of channels. Range could be suggested or absolute as not all spaces have definitive ranges.
    BOUNDS = tuple()  # type: Tuple[Bounds, ...]
    # White point
    WHITE = "D50"

    def __init__(self, color: Union['Space', Vector], alpha: Optional[float] = None) -> None:
        """Initialize."""

        num_channels = len(self.CHANNEL_NAMES)
        self._alpha = util.NaN
        self._coords = [util.NaN] * num_channels

        if isinstance(color, Space):
            for index, channel in enumerate(color.coords()):
                setattr(self, self.CHANNEL_NAMES[index], channel)
            self.alpha = color.alpha
        elif isinstance(color, Sequence):
            if len(color) != num_channels:  # pragma: no cover
                # Only likely to happen with direct usage internally.
                raise ValueError(
                    "A list of channel values should be at a minimum of {}.".format(num_channels)
                )
            for index in range(num_channels):
                setattr(self, self.CHANNEL_NAMES[index], color[index])
            self.alpha = 1.0 if alpha is None else alpha
        else:  # pragma: no cover
            # Only likely to happen with direct usage internally.
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    def __repr__(self) -> str:
        """Representation."""

        values = [util.fmt_float(coord, util.DEF_PREC) for coord in self.coords()]

        return 'color({} {} / {})'.format(
            self._serialize()[0],
            ' '.join(values),
            util.fmt_float(util.no_nan(self.alpha), util.DEF_PREC)
        )

    __str__ = __repr__

    def _handle_input(self, value: float) -> float:
        """Handle numerical input."""

        if not util.is_number(value):
            raise TypeError("Value should be a number not type '{}'".format(type(value)))
        return float(value)

    def coords(self) -> MutableVector:
        """Coordinates."""

        return self._coords[:]

    @classmethod
    def _serialize(cls) -> Tuple[str, ...]:
        """Get the serialized name."""

        return (cls.NAME,) if not cls.SERIALIZE else cls.SERIALIZE

    @classmethod
    def white(cls) -> MutableVector:
        """Get the white color for this color space."""

        return list(WHITES[cls.WHITE])

    @property
    def alpha(self) -> float:
        """Alpha channel."""

        return self._alpha

    @alpha.setter
    def alpha(self, value: float) -> None:
        """Adjust alpha."""

        self._alpha = util.clamp(self._handle_input(value), 0.0, 1.0)

    def set(self, name: str, value: float) -> 'Space':  # noqa: A003
        """Set the given channel."""

        name = self.CHANNEL_ALIASES.get(name, name)
        if name not in self.CHANNEL_NAMES and name != 'alpha':
            raise AttributeError("'{}' is an invalid channel name".format(name))

        setattr(self, name, value)
        return self

    def get(self, name: str) -> float:
        """Get the given channel's value."""

        name = self.CHANNEL_ALIASES.get(name, name)
        if name not in self.CHANNEL_NAMES and name != 'alpha':
            raise AttributeError("'{}' is an invalid channel name".format(name))
        return cast(float, getattr(self, name))

    @classmethod
    @abstractmethod
    def to_base(cls, coords: MutableVector) -> MutableVector:  # pragma: no cover
        """To base color."""

    @classmethod
    @abstractmethod
    def from_base(cls, coords: MutableVector) -> MutableVector:  # pragma: no cover
        """From base color."""

    def to_string(
        self,
        parent: 'Color',
        *,
        alpha: Optional[bool] = None,
        precision: Optional[int] = None,
        fit: Union[bool, str] = True,
        none: bool = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS 'color' string: `color(space coords+ / alpha)`."""

        if precision is None:
            precision = parent.PRECISION

        a = util.no_nan(self.alpha) if not none else self.alpha
        alpha = alpha is not False and (alpha is True or a < 1.0 or util.is_nan(a))

        method = None if not isinstance(fit, str) else fit
        coords = parent.fit(method=method).coords() if fit else self.coords()
        if not none:
            coords = util.no_nans(coords)

        values = [util.fmt_float(coord, precision) for coord in coords]

        if alpha:
            return "color({} {} / {})".format(
                self._serialize()[0], ' '.join(values), util.fmt_float(a, max(precision, util.DEF_PREC))
            )
        else:
            return "color({} {})".format(self._serialize()[0], ' '.join(values))

    @classmethod
    def null_adjust(cls, coords: MutableVector, alpha: float) -> Tuple[MutableVector, float]:
        """Process coordinates and adjust any channels to null/NaN if required."""

        return coords, alpha

    @classmethod
    def match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> Optional[Tuple[Tuple[MutableVector, float], int]]:
        """Match a color by string."""

        m = cast(Pattern[str], cls.DEFAULT_MATCH).match(string, start)
        if (
            m is not None and
            (
                (m.group(1) and m.group(1).lower() in cls._serialize())
            ) and (not fullmatch or m.end(0) == len(string))
        ):

            # Break channels up into a list
            num_channels = len(cls.CHANNEL_NAMES)
            split = parse.RE_SLASH_SPLIT.split(m.group(2).strip(), maxsplit=1)

            # Get alpha channel
            alpha = parse.norm_alpha_channel(split[-1].lower()) if len(split) > 1 else 1.0

            # Parse color channels
            channels = []
            for i, c in enumerate(parse.RE_CHAN_SPLIT.split(split[0]), 0):
                if c and i < num_channels:
                    # If the channel is a percentage, force it to scale from 0 - 100, not 0 - 1.
                    is_percent = cls.BOUNDS[i].flags & FLG_PERCENT
                    channels.append(parse.norm_color_channel(c.lower(), not is_percent))

            # Missing channels are filled with `NaN`
            if len(channels) < num_channels:
                diff = num_channels - len(channels)
                channels.extend([util.NaN] * diff)

            # Apply null adjustments (null hues) if applicable
            return (channels, alpha), m.end(0)

        return None
