"""Gamut handling."""
from .. import algebra as alg
from ..channels import FLG_ANGLE
from abc import ABCMeta, abstractmethod
from ..types import Plugin
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def clip_channels(color: 'Color') -> None:
    """Clip channels."""

    channels = alg.no_nans(color[:-1])

    for i, value in enumerate(channels):
        chan = color._space.CHANNELS[i]
        a = chan.low  # type: Optional[float]
        b = chan.high  # type: Optional[float]

        # Wrap the angle. Not technically out of gamut, but we will clean it up.
        if chan.flags & FLG_ANGLE:
            color[i] = value % 360.0
            continue

        # These parameters are unbounded
        if not chan.bound:  # pragma: no cover
            # Will not execute unless we have a space that defines some coordinates
            # as bound and others as not. We do not currently have such spaces.
            a = b = None

        # Fit value in bounds.
        color[i] = alg.clamp(value, a, b)


def verify(color: 'Color', tolerance: float) -> bool:
    """Verify the values are in bound."""

    channels = alg.no_nans(color[:-1])
    for i, value in enumerate(channels):
        chan = color._space.CHANNELS[i]
        a = chan.low  # type: Optional[float]
        b = chan.high  # type: Optional[float]

        # Angles will wrap, so no sense checking them
        if chan.flags & FLG_ANGLE:
            continue

        # These parameters are unbounded
        if not chan.bound:
            a = b = None

        # Check if bounded values are in bounds
        if (a is not None and value < (a - tolerance)) or (b is not None and value > (b + tolerance)):
            return False
    return True


class Fit(Plugin, metaclass=ABCMeta):
    """Fit plugin class."""

    NAME = ''

    @abstractmethod
    def fit(self, color: 'Color', **kwargs: Any) -> None:
        """Get coordinates of the new gamut mapped color."""
