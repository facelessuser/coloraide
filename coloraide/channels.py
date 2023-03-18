"""Channels."""
from __future__ import annotations

FLG_ANGLE = 1
FLG_PERCENT = 2
FLG_OPT_PERCENT = 4
FLG_MIRROR_PERCENT = 8


class Channel(str):
    """Channel."""

    low: float
    high: float
    span: float
    offset: float
    bound: bool
    flags: int
    limit: tuple[float | None, float | None]
    nans: float

    def __new__(
        cls,
        name: str,
        low: float,
        high: float,
        mirror_range: bool = False,
        bound: bool = False,
        flags: int = 0,
        limit: tuple[float | None, float | None] = (None, None),
        nans: float = 0.0
    ) -> 'Channel':
        """Initialize."""

        obj = super().__new__(cls, name)
        obj.low = low
        obj.high = high
        mirror = flags & FLG_MIRROR_PERCENT and abs(low) == high
        obj.span = high if mirror else high - low
        obj.offset = 0.0 if mirror else -low
        obj.bound = bound
        obj.flags = flags
        obj.limit = limit
        obj.nans = nans

        return obj
