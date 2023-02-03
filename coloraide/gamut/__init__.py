"""Gamut handling."""
from __future__ import annotations
from .. import algebra as alg
from ..channels import FLG_ANGLE
from abc import ABCMeta, abstractmethod
from ..types import Plugin
from typing import TYPE_CHECKING, Any
from .. import util

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def clip_channels(color: Color) -> None:
    """Clip channels."""

    for i, value in enumerate(color[:-1]):

        chan = color._space.CHANNELS[i]

        # Wrap the angle. Not technically out of gamut, but we will clean it up.
        if chan.flags & FLG_ANGLE:
            color[i] = util.constrain_hue(value)

        # Ignore undefined or unbounded channels
        if not chan.bound or alg.is_nan(value):
            continue

        # Fit value in bounds.
        color[i] = alg.clamp(value, chan.low, chan.high)


def verify(color: Color, tolerance: float) -> bool:
    """Verify the values are in bound."""

    for i, value in enumerate(color[:-1]):
        chan = color._space.CHANNELS[i]

        # Ignore undefined channels, angles which wrap, and unbounded channels
        if chan.flags & FLG_ANGLE or not chan.bound or alg.is_nan(value):
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
