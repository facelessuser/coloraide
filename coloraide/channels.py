"""Channels."""
from __future__ import annotations
import math
from typing import Callable
from . import algebra as alg

FLG_ANGLE = 1
FLG_PERCENT = 2
FLG_OPT_PERCENT = 4
FLG_MIRROR_PERCENT = 8
HUE_NULL = 0
HUE_DEG = 1
HUE_RAD = 2
HUE_GRAD = 3
HUE_TURN = 4

HUE_RANGE = {
    HUE_DEG: (0.0, 360.0),
    HUE_RAD: (0.0, math.tau),
    HUE_GRAD: (0.0, 400),
    HUE_TURN: (0.0, 1.0)
}


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
    hue: int

    def __new__(
        cls,
        name: str,
        low: float,
        high: float,
        bound: bool = False,
        flags: int = 0,
        limit: Callable[[float], float | int] | tuple[float | None, float | None] | None = None,
        nans: float = 0.0,
        hue: int = HUE_NULL
    ) -> Channel:
        """Initialize."""

        obj = super().__new__(cls, name)
        obj.bound = bound
        obj.flags = flags
        obj.hue = (HUE_DEG if hue == HUE_NULL else hue) if flags & FLG_ANGLE else HUE_NULL
        if obj.hue:
            obj.low = HUE_RANGE[obj.hue][0]
            obj.high = HUE_RANGE[obj.hue][1]
        else:
            obj.low = low
            obj.high = high
        mirror = flags & FLG_MIRROR_PERCENT and abs(low) == high
        obj.span = high if mirror else high - low
        obj.offset = 0.0 if mirror else -low
        # If nothing is provided, assume casting to float
        if limit is None:
            limit = float
        # If a tuple of min/max is provided, create a function to clamp to the range
        elif isinstance(limit, tuple):
            limit = lambda x, l=limit: float(alg.clamp(x, l[0], l[1]))  # type: ignore[misc]
        obj.limit = limit
        obj.nans = nans

        return obj
