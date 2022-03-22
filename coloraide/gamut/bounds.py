"""Channel boundary objects."""
from typing import Any

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
