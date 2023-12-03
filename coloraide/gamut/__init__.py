"""Gamut handling."""
from __future__ import annotations
import math
from ..channels import FLG_ANGLE
from abc import ABCMeta, abstractmethod
from ..types import Plugin
from typing import TYPE_CHECKING, Any
from .. import util
from . import pointer

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

__all__ = ('clip_channels', 'verify', 'Fit', 'pointer')


def clip_channels(color: Color, nans: bool = True) -> bool:
    """Clip channels."""

    clipped = False

    for i, value in enumerate(color[:-1]):

        chan = color._space.CHANNELS[i]

        # Wrap the angle. Not technically out of gamut, but we will clean it up.
        if chan.flags & FLG_ANGLE:
            color[i] = util.constrain_hue(value)
            continue

        # Ignore undefined or unbounded channels
        if not chan.bound or math.isnan(value):
            continue

        # Fit value in bounds.
        if value < chan.low:
            color[i] = chan.low
        elif value > chan.high:
            color[i] = chan.high
        else:
            continue

        clipped = True

    return clipped


def verify(color: Color, tolerance: float) -> bool:
    """Verify the values are in bound."""

    for i, value in enumerate(color[:-1]):
        chan = color._space.CHANNELS[i]

        # Ignore undefined channels, angles which wrap, and unbounded channels
        if chan.flags & FLG_ANGLE or not chan.bound or math.isnan(value):
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
    def fit(self, color: Color, **kwargs: Any) -> None:
        """Get coordinates of the new gamut mapped color."""
