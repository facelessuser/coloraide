"""Color base."""
import re
from abc import ABCMeta, abstractmethod
from .. import util
from ..util import Vector, MutableVector
from .. import parse
from typing import Tuple, Dict, Optional, Union, Sequence, Any, List, cast, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

# TODO: Before 1.0, merge this with the statement below as color spaces will not need this moving forward.
RE_DEFAULT_MATCH = r"""(?xi)
color\(\s*
({{color_space}})
((?:{space}(?:{strict_percent}|{float})){{{{{{channels}}}}}}(?:{slash}(?:{strict_percent}|{float}))?)
\s*\)
""".format(
    **parse.COLOR_PARTS
)

# Allow 10 channels maximum. This should be able to handle any colors we throw at it.
RE_COLOR_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='-{0,2}[a-z][-a-z0-9_]*', channels='1,10'))

# From CIE 2004 Colorimetry T.3 and T.8
# B from https://en.wikipedia.org/wiki/Standard_illuminant#White_point
WHITES = {
    "2deg": {
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
    },

    "10deg": {
        "A": (0.45117, 0.40594),
        "B": (0.34980, 0.35270),
        "C": (0.31039, 0.31905),
        "D50": (0.34773, 0.35952),
        "D55": (0.33412, 0.34877),
        "D65": (0.31382, 0.33100),
        "D75": (0.29968, 0.31740),
        "E": (1 / 3, 1 / 3),
        "F2": (0.37925, 0.36733),
        "F3": (0.41761, 0.38324),
        "F11": (0.38541, 0.37123)
    }
}

FLG_ANGLE = 0x1
FLG_PERCENT = 0x2
FLG_OPT_PERCENT = 0x4


def color_match(
    string: str,
    spaces: Dict[str, Type['Space']],
    start: int,
    fullmatch: bool = False
) -> Optional[Tuple[Type['Space'], Tuple[MutableVector, float], int]]:
    """Perform default color matching."""

    m = RE_COLOR_MATCH.match(string, start)
    if m is not None and (not fullmatch or m.end(0) == len(string)):
        ident = m.group(1).lower()

        # Iterate the spaces and see if we find the color serialization identifier
        for space in spaces.values():
            if ident in space._serialize():
                # Break channels up into a list
                num_channels = len(space.CHANNEL_NAMES)
                split = parse.RE_SLASH_SPLIT.split(m.group(2).strip(), maxsplit=1)

                # Get alpha channel
                alpha = parse.norm_alpha_channel(split[-1].lower()) if len(split) > 1 else 1.0

                # Parse color channels
                channels = []
                i = -1
                for i, c in enumerate(parse.RE_CHAN_SPLIT.split(split[0]), 0):
                    if c and i < num_channels:
                        # If the channel is a percentage, force it to scale from 0 - 100, not 0 - 1.
                        is_percent = space.BOUNDS[i].flags & FLG_PERCENT
                        channels.append(parse.norm_color_channel(c.lower(), not is_percent))
                    else:
                        # Not the right amount of channels
                        break

                # Apply null adjustments (null hues) if applicable
                # or return None if we got the wrong amount of channels
                if i + 1 == num_channels:
                    return space, (channels, alpha), m.end(0)
                break
    return None


def color_serialize(
    space: 'Space',
    parent: Optional['Color'],
    **kwargs: Any
) -> str:
    """Convert to CSS 'color' string: `color(space coords+ / alpha)`."""

    # Get precision
    precision = kwargs.get('precision')
    if precision is None:
        precision = parent.PRECISION if parent else util.DEF_PREC

    # Get if alpha and allow 'none' if desired
    none = kwargs.get('none', False)
    a = util.no_nan(space.alpha) if not none else space.alpha

    # Determine if we should show alpha
    alpha = kwargs.get('alpha')
    alpha = alpha is not False and (alpha is True or a < 1.0 or util.is_nan(a))

    # Get coordinates and fit if desired. Allow 'none' if desired.
    fit = kwargs.get('fit', True)
    method = None if not isinstance(fit, str) else fit
    coords = parent.fit(method=method).coords() if parent and fit else space.coords()
    if not none:
        coords = util.no_nans(coords)

    # Print at the desired precision showing alpha if required
    values = [util.fmt_float(coord, precision) for coord in coords]
    if alpha:
        return "color({} {} / {})".format(
            space._serialize()[0], ' '.join(values), util.fmt_float(a, max(precision, util.DEF_PREC))
        )
    else:
        return "color({} {})".format(space._serialize()[0], ' '.join(values))


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
    # Enable or disable default color format parsing and serialization.
    COLOR_FORMAT = True
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
    WHITE = (0.0, 0.0)

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
                    "{} accepts a list of {} channels".format(self.NAME, num_channels)
                )
            for index in range(num_channels):
                util.assert_number(color[index])
                setattr(self, self.CHANNEL_NAMES[index], color[index])
            self.alpha = 1.0 if alpha is None else alpha
        else:  # pragma: no cover
            # Only likely to happen with direct usage internally.
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    def __repr__(self) -> str:
        """Representation."""

        return color_serialize(self, None, alpha=True, none=True, precision=util.DEF_PREC)

    __str__ = __repr__

    def coords(self) -> MutableVector:
        """Coordinates."""

        return self._coords[:]

    @classmethod
    def _serialize(cls) -> Tuple[str, ...]:
        """Get the serialized name."""

        return (cls.NAME,) if not cls.SERIALIZE else cls.SERIALIZE

    @classmethod
    def white(cls) -> Vector:
        """Get the white color for this color space."""

        return cls.WHITE

    @property
    def alpha(self) -> float:
        """Alpha channel."""

        return self._alpha

    @alpha.setter
    def alpha(self, value: float) -> None:
        """Adjust alpha."""

        self._alpha = util.clamp(value, 0.0, 1.0)

    def set(self, name: str, value: float) -> None:  # noqa: A003
        """Set the given channel."""

        name = self.CHANNEL_ALIASES.get(name, name)
        if name not in self.CHANNEL_NAMES and name != 'alpha':
            raise AttributeError("'{}' is an invalid channel name".format(name))

        util.assert_number(value)

        setattr(self, name, value)

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

        return color_serialize(self, parent, alpha=alpha, precision=precision, fit=fit, none=none)

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

        return None
