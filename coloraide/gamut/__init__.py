"""Gamut handling."""
from .. import util
from ..spaces import FLG_ANGLE, GamutBound
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def clip_channels(color: 'Color') -> None:
    """Clip channels."""

    channels = util.no_nans(color.coords())
    fit = []

    for i, value in enumerate(channels):
        bounds = color._space.BOUNDS[i]
        a = bounds.lower  # type: Optional[float]
        b = bounds.upper  # type: Optional[float]
        is_bound = isinstance(bounds, GamutBound)

        # Wrap the angle. Not technically out of gamut, but we will clean it up.
        if bounds.flags & FLG_ANGLE:
            fit.append(value % 360.0)
            continue

        # These parameters are unbounded
        if not is_bound:  # pragma: no cover
            # Will not execute unless we have a space that defines some coordinates
            # as bound and others as not. We do not currently have such spaces.
            a = b = None

        # Fit value in bounds.
        fit.append(util.clamp(value, a, b))
    color.update(color.space(), fit, color.alpha)


def verify(color: 'Color', tolerance: float) -> bool:
    """Verify the values are in bound."""

    channels = util.no_nans(color.coords())
    for i, value in enumerate(channels):
        bounds = color._space.BOUNDS[i]
        a = bounds.lower  # type: Optional[float]
        b = bounds.upper  # type: Optional[float]
        is_bound = isinstance(bounds, GamutBound)

        # Angles will wrap, so no sense checking them
        if bounds.flags & FLG_ANGLE:
            continue

        # These parameters are unbounded
        if not is_bound:
            a = b = None

        # Check if bounded values are in bounds
        if (a is not None and value < (a - tolerance)) or (b is not None and value > (b + tolerance)):
            return False
    return True


class Fit(ABCMeta):
    """Fit plugin class."""

    NAME = ''

    @classmethod
    @abstractmethod
    def fit(cls, color: 'Color', **kwargs: Any) -> None:
        """Get coordinates of the new gamut mapped color."""
