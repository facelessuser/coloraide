"""Clip to fit in gamut."""
from ... import util
from ... spaces import Angle, GamutBound


def fit(color):
    """Gamut clipping."""

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
