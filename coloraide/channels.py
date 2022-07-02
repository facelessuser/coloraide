"""Channels."""
from typing import Tuple, Optional

FLG_ANGLE = 1
FLG_PERCENT = 2
FLG_OPT_PERCENT = 4


class Channel(str):
    """Channel."""

    low: float
    high: float
    bound: bool
    flags: int
    limit: Tuple[Optional[float], Optional[float]]

    def __new__(
        cls,
        name: str,
        low: float,
        high: float,
        bound: bool = False,
        flags: int = 0,
        limit: Tuple[Optional[float], Optional[float]] = (None, None)
    ) -> 'Channel':
        """Initialize."""

        obj = super().__new__(cls, name)
        obj.low = low
        obj.high = high
        obj.bound = bound
        obj.flags = flags
        obj.limit = limit

        return obj
