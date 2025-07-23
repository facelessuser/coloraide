"""Channels."""
from __future__ import annotations
from typing import Callable
from . import algebra as alg

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
    limit: Callable[[float], float | int]
    nans: float

    def __new__(
        cls,
        name: str,
        low: float,
        high: float,
        bound: bool = False,
        flags: int = 0,
        limit: Callable[[float], float | int] | tuple[float | None, float | None] | None = None,
        nans: float = 0.0
    ) -> Channel:
        """Initialize."""

        obj = super().__new__(cls, name)
        obj.low = low
        obj.high = high
        mirror = flags & FLG_MIRROR_PERCENT and abs(low) == high
        obj.span = high if mirror else high - low
        obj.offset = 0.0 if mirror else -low
        obj.bound = bound
        obj.flags = flags
        # If nothing is provided, assume casting to float
        if limit is None:
            limit = float
        # If a tuple of min/max is provided, create a function to clamp to the range
        elif isinstance(limit, tuple):
            limit = lambda x, l=limit: float(alg.clamp(x, l[0], l[1]))  # type: ignore[misc]
        obj.limit = limit
        obj.nans = nans

        return obj
