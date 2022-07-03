"""Color base."""
from abc import ABCMeta, abstractmethod
from .. import cat
from ..css import parse
from ..channels import Channel
from ..css import serialize
from .. import algebra as alg
from ..types import VectorLike, Vector, Plugin
from typing import Tuple, Dict, Optional, Union, Any, List, cast, Type, Iterator, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

# TODO: Remove for before 1.0.
# Here only to prevent breakage.
RE_DEFAULT_MATCH = parse.RE_DEFAULT_MATCH
WHITES = cat.WHITES


class Cylindrical:
    """Cylindrical space."""

    @classmethod
    def hue_name(cls) -> str:
        """Hue channel name."""

        return "h"

    @classmethod
    def hue_index(cls) -> int:  # pragma: no cover
        """Get hue index."""

        return cast(Type['Space'], cls).get_channel_index(cls.hue_name())


class Labish:
    """Lab-ish color spaces."""

    @classmethod
    def labish_names(cls) -> Tuple[str, ...]:
        """Return Lab-ish names in the order L a b."""

        return cast(Type['Space'], cls).CHANNELS

    @classmethod
    def labish_indexes(cls) -> List[int]:  # pragma: no cover
        """Return the index of the Lab-ish channels."""

        names = cls.labish_names()
        return [cast(Type['Space'], cls).get_channel_index(name) for name in names]


class Lchish(Cylindrical):
    """Lch-ish color spaces."""

    @classmethod
    def lchish_names(cls) -> Tuple[str, ...]:  # pragma: no cover
        """Return Lch-ish names in the order L c h."""

        return cast(Type['Space'], cls).CHANNELS

    @classmethod
    def lchish_indexes(cls) -> List[int]:  # pragma: no cover
        """Return the index of the Lab-ish channels."""

        names = cls.lchish_names()
        return [cast(Type['Space'], cls).get_channel_index(name) for name in names]


alpha_channel = Channel('alpha', 0.0, 1.0, bound=True, limit=(0.0, 1.0))


class SpaceMeta(ABCMeta):
    """Ensure on subclass that the subclass has new instances of mappings."""

    def __init__(cls, name: str, bases: Tuple[object, ...], clsdict: Dict[str, Any]) -> None:
        """Copy mappings on subclass."""

        if len(cls.mro()) > 2:
            cls.CHANNEL_ALIASES = cls.CHANNEL_ALIASES.copy()  # type: Dict[str, str]


class Space(Plugin, metaclass=SpaceMeta):
    """Base color space object."""

    BASE = ""  # type: str
    # Color space name
    NAME = ""
    # Serialized name
    SERIALIZE = tuple()  # type: Tuple[str, ...]
    # Channel names
    CHANNELS = tuple()  # type: Tuple[Channel, ...]
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
    # White point
    WHITE = (0.0, 0.0)

    @classmethod
    def get_channel_index(cls, name: str) -> int:
        """Get channel index."""

        if name == 'alpha':
            return len(cls.CHANNELS)
        return cls.CHANNELS.index(cls.CHANNEL_ALIASES.get(name, name))

    @classmethod
    def get_channel(cls, index: int) -> Channel:
        """Get channel index."""

        return (cls.CHANNELS + (alpha_channel,))[index]

    @classmethod
    def get_all_channels(cls) -> Iterator[Channel]:
        """Get all channels."""

        yield from cls.CHANNELS
        yield alpha_channel

    @classmethod
    def _serialize(cls) -> Tuple[str, ...]:
        """Get the serialized name."""

        return (cls.NAME,) if not cls.SERIALIZE else cls.SERIALIZE

    @classmethod
    def white(cls) -> VectorLike:
        """Get the white color for this color space."""

        return cls.WHITE

    @classmethod
    @abstractmethod
    def to_base(cls, coords: Vector) -> Vector:  # pragma: no cover
        """To base color."""

    @classmethod
    @abstractmethod
    def from_base(cls, coords: Vector) -> Vector:  # pragma: no cover
        """From base color."""

    @classmethod
    def to_string(
        cls,
        parent: 'Color',
        *,
        alpha: Optional[bool] = None,
        precision: Optional[int] = None,
        fit: Union[bool, str] = True,
        none: bool = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS 'color' string: `color(space coords+ / alpha)`."""

        return serialize.serialize_css(
            parent,
            color=True,
            alpha=alpha,
            precision=precision,
            fit=fit,
            none=none
        )

    @classmethod
    def normalize(cls, coords: Vector) -> Vector:
        """Process coordinates and adjust any channels to null/NaN if required."""

        return alg.no_nans(coords)

    @classmethod
    def match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> Optional[Tuple[Tuple[Vector, float], int]]:
        """Match a color by string."""

        return None
