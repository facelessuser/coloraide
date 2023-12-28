"""Gamut handling."""
from __future__ import annotations
import math
from ..channels import FLG_ANGLE
from abc import ABCMeta, abstractmethod
from ..types import Plugin
from typing import TYPE_CHECKING, Any
from . import pointer

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

__all__ = ('clip_channels', 'verify', 'Fit', 'pointer')


def clip_channels(color: Color, nans: bool = True) -> bool:
    """Clip channels."""

    clipped = False

    cs = color._space
    for i, value in enumerate(cs.normalize(color[:-1])):

        chan = cs.CHANNELS[i]

        # Ignore angles, undefined, or unbounded channels
        if not chan.bound or math.isnan(value) or chan.flags & FLG_ANGLE:
            color[i] = value
            continue

        # Fit value in bounds.
        if value < chan.low:
            color[i] = chan.low
        elif value > chan.high:
            color[i] = chan.high
        else:
            color[i] = value
            continue

        clipped = True

    return clipped


def verify(color: Color, tolerance: float) -> bool:
    """Verify the values are in bound."""

    cs = color._space
    for i, value in enumerate(cs.normalize(color[:-1])):
        chan = cs.CHANNELS[i]

        # Ignore undefined channels, angles which wrap, and unbounded channels
        if not chan.bound or math.isnan(value) or chan.flags & FLG_ANGLE:
            continue

        a = chan.low
        b = chan.high

        # Check if bounded values are in bounds
        if (a is not None and value < (a - tolerance)) or (b is not None and value > (b + tolerance)):
            return False
    return True


class Fit(Plugin, metaclass=ABCMeta):
    """Fit plugin class."""

    NAME = ''

    @abstractmethod
    def fit(self, color: Color, space: str, **kwargs: Any) -> None:
        """Get coordinates of the new gamut mapped color."""
