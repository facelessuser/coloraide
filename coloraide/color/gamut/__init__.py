"""Gamut handling."""
from ... import util
from ... spaces import Angle, GamutBound
from abc import ABCMeta, abstractmethod


def clip_channels(color):
    """Clip channels."""

    channels = util.no_nan(color.coords())
    gamut = color._space.RANGE
    fit = []

    for i, value in enumerate(channels):
        a, b = gamut[i]
        is_bound = isinstance(gamut[i], GamutBound)

        # Wrap the angle. Not technically out of gamut, but we will clean it up.
        if isinstance(a, Angle) and isinstance(b, Angle):
            fit.append(value % 360.0)
            continue

        # These parameters are unbounded
        if not is_bound:  # pragma: no cover
            # Will not execute unless we have a space that defines some coordinates
            # as bound and others as not. We do not currently have such spaces.
            a = None
            b = None

        # Fit value in bounds.
        fit.append(util.clamp(value, a, b))
    return fit


def verify(color, tolerance):
    """Verify the values are in bound."""

    channels = util.no_nan(color.coords())
    for i, value in enumerate(channels):
        a, b = color._space.RANGE[i]
        is_bound = isinstance(color._space.RANGE[i], GamutBound)

        # Angles will wrap, so no sense checking them
        if isinstance(a, Angle):
            continue

        # These parameters are unbounded
        if not is_bound:
            a = None
            b = None

        # Check if bounded values are in bounds
        if (a is not None and value < (a - tolerance)) or (b is not None and value > (b + tolerance)):
            return False
    return True


class Fit(ABCMeta):
    """Fit plugin class."""

    @staticmethod
    @abstractmethod
    def name():
        """Get name of method."""

    @staticmethod
    @abstractmethod
    def distance(color):
        """Get coordinates of the new gamut mapped color."""
