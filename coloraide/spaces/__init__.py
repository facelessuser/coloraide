"""Color base."""
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from ..channels import Channel
from ..css import serialize
from ..types import VectorLike, Vector, Plugin
from typing import Any, TYPE_CHECKING, Callable, Sequence
import math

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class Regular:
    """Regular 3D color space usually with a range between 0 - 1."""

    channels: tuple[Channel, ...]
    get_channel_index: Callable[[str], int]


class Cylindrical:
    """Cylindrical space."""

    channels: tuple[Channel, ...]
    get_channel_index: Callable[[str], int]
    get_hue_name: Callable[[], str]
    get_radial_name: Callable[[], str]

    def radial_name(self) -> str:
        """Radial name."""

        return "s"

    def hue_name(self) -> str:
        """Hue channel name."""

        return "h"

    def hue_index(self) -> int:  # pragma: no cover
        """Get hue index."""

        return self.get_channel_index(self.hue_name())

    def radial_index(self) -> int:  # pragma: no cover
        """Get radial index."""

        return self.get_channel_index(self.radial_name())


class RGBish(Regular):
    """RGB-ish space."""

    def names(self) -> tuple[Channel, ...]:
        """Return RGB-ish names in order R G B."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of RGB-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]

    def linear(self) -> str:
        """Will return the name of the space which is the linear version of itself (if available)."""

        return ''


class HSLish(Cylindrical):
    """HSL-ish space."""

    def names(self) -> tuple[Channel, ...]:
        """Return HSL-ish names in order H S L."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of HSL-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]


class HSVish(Cylindrical):
    """HSV-ish space."""

    def names(self) -> tuple[Channel, ...]:
        """Return HSV-ish names in order H S V."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of HSV-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]


class HWBish(Cylindrical):
    """HWB-ish space."""

    def radial_name(self) -> str:
        """Radial name."""

        return "w"

    def names(self) -> tuple[Channel, ...]:
        """Return HWB-ish names in order H W B."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of HWB-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]


class Labish:
    """Lab-ish color spaces."""

    channels: tuple[Channel, ...]
    get_channel_index: Callable[[str], int]

    def names(self) -> tuple[Channel, ...]:
        """Return Lab-ish names in the order L a b."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of the Lab-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]


class LChish(Cylindrical):
    """LCh-ish color spaces."""

    def radial_name(self) -> str:
        """Radial name."""

        return "c"

    def names(self) -> tuple[Channel, ...]:
        """Return LCh-ish names in the order L c h."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of the Lab-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]


alpha_channel = Channel('alpha', 0.0, 1.0, bound=True, limit=(0.0, 1.0))


class SpaceMeta(ABCMeta):
    """Ensure on subclass that the subclass has new instances of mappings."""

    def __init__(cls, name: str, bases: tuple[object, ...], clsdict: dict[str, Any]) -> None:
        """Copy mappings on subclass."""

        if len(cls.mro()) > 2:
            cls.CHANNEL_ALIASES = cls.CHANNEL_ALIASES.copy()  # type: dict[str, str]


class Space(Plugin, metaclass=SpaceMeta):
    """Base color space object."""

    BASE = ""  # type: str
    # Color space name
    NAME = ""
    # Serialized name
    SERIALIZE = ()  # type: tuple[str, ...]
    # Channel names
    CHANNELS = ()  # type: tuple[Channel, ...]
    # Channel aliases
    CHANNEL_ALIASES = {}  # type: dict[str, str]
    # Enable or disable default color format parsing and serialization.
    COLOR_FORMAT = True
    # Some color spaces are a transform of a specific RGB color space gamut, e.g. HSL has a gamut of sRGB.
    # When testing or gamut mapping a color within the current color space's gamut, `GAMUT_CHECK` will
    # declare which space must be used as reference if anything other than the current space is required.
    #
    # Specifically, when testing if a color is in gamut, both the origin space and the specified gamut
    # space will be checked as sometimes a color is within the threshold of being "close enough" to the gamut,
    # but the color can still be far outside the origin space's coordinates. Checking both ensures sane values
    # that are also close enough to the gamut.
    #
    # When actually gamut mapping, only the gamut space is used, if none is specified, the origin space is used.
    GAMUT_CHECK = None  # type: str | None
    # `CLIP_SPACE` forces a different space to be used for clipping than what is specified by `GAMUT_CHECK`.
    # This is used in cases like HSL where the `GAMUT_CHECK` space is sRGB, but we want to clip in HSL as it
    # is still reasonable and faster.
    CLIP_SPACE = None  # type: str | None
    # When set to `True`, this denotes that the color space has the ability to represent out of gamut in colors in an
    # extended range. When interpolation is done, if colors are interpolated in a smaller gamut than the colors being
    # interpolated, the colors will usually be gamut mapped, but if the interpolation space happens to support extended
    # ranges, then the colors will not be gamut mapped even if their gamut is larger than the target interpolation
    # space.
    EXTENDED_RANGE = False
    # White point
    WHITE = (0.0, 0.0)
    # What is the color space's dynamic range
    DYNAMIC_RANGE = 'sdr'

    def __init__(self, **kwargs: Any) -> None:
        """Initialize."""

        self.channels = self.CHANNELS + (alpha_channel,)
        self._chan_index = {c: e for e, c in enumerate(self.channels)}  # type: dict[str, int]
        self._color_ids = (self.NAME,) if not self.SERIALIZE else self.SERIALIZE
        self._percents = ([True] * (len(self.channels) - 1)) + [False]
        self._polar = isinstance(self, Cylindrical)

    def is_polar(self) -> bool:
        """Return if the space is polar."""

        return self._polar

    def get_channel_index(self, name: str) -> int:
        """Get channel index."""

        idx = self._chan_index.get(self.CHANNEL_ALIASES.get(name, name))
        return int(name) if idx is None else idx

    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resolve channels."""

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value

    def _serialize(self) -> tuple[str, ...]:
        """Get the serialized name."""

        return self._color_ids

    def normalize(self, coords: Vector) -> Vector:
        """
        Normalize coordinates.

        This allows a color space to normalize valid, but non-standard coordinates.
        An example is cylindrical spaces with negative chroma/saturation. Such models
        often have a valid, positive chroma/saturation and hue configuration that
        matches the same color.
        """

        return coords

    def is_achromatic(self, coords: Vector) -> bool | None:  # pragma: no cover
        """Check if color is achromatic."""

        return None

    @classmethod
    def white(cls) -> VectorLike:
        """Get the white color for this color space."""

        return cls.WHITE

    @abstractmethod
    def to_base(self, coords: Vector) -> Vector:  # pragma: no cover
        """To base color."""

    @abstractmethod
    def from_base(self, coords: Vector) -> Vector:  # pragma: no cover
        """From base color."""

    def to_string(
        self,
        parent: Color,
        *,
        alpha: bool | None = None,
        precision: int | Sequence[int] | None = None,
        fit: str | bool | dict[str, Any] = True,
        none: bool = False,
        percent: bool | Sequence[bool] = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS 'color' string: `color(space coords+ / alpha)`."""

        return serialize.serialize_css(
            parent,
            color=True,
            alpha=alpha,
            precision=precision,
            fit=fit,
            none=none,
            percent=percent
        )

    def match(
        self,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> tuple[tuple[Vector, float], int] | None:
        """Match a color by string."""

        return None
