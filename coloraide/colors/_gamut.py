"""Gamut handling."""
from .. import util

THRESHOLD = 0.000075


class GamutHue(float):
    """Gamut hue."""


class GamutBound(float):
    """Bounded gamut value."""


class GamutUnbound(float):
    """Unbounded gamut value."""


def gamut_clip(obj):
    """Gamut clipping."""

    channels = obj._channels
    gamut = obj._gamut
    fit = []

    for i, value in enumerate(channels):
        a, b = gamut[i]

        # Normalize hue
        if isinstance(a, GamutHue) and isinstance(b, GamutHue):
            fit.append(value if 0.0 <= value <= 360.0 else value % 360.0)
            continue

        # These parameters are unbounded
        if isinstance(a, GamutUnbound):
            a = None
        if isinstance(b, GamutUnbound):
            b = None

        if (a is not None and value < (a - THRESHOLD)) or (b is not None and value > (b + THRESHOLD)):
            fit.append(util.clamp(value, a, b))
        else:
            fit.append(value)
    return fit


class _Gamut:
    """Gamut handling."""

    def fit_gamut(self, space=None, method=gamut_clip):
        """Fit the gamut using the provided method."""

        if space is not None:
            c = self.convert(space)
            c.fit_gamut(method=method)
            self.mutate(c)
        else:
            fit = method(self)
            for i in range(len(fit)):
                self._channels[i] = fit[i]

    def in_gamut(self, space=None):
        """Check if current color is in gamut."""

        if space is not None:
            c = self.convert(space)
            return c.in_gamut()

        channels = self._channels
        for i, value in enumerate(channels):
            a, b = self._gamut[i]

            # Normalize hue
            if isinstance(a, GamutHue) and isinstance(b, GamutHue):
                continue

            # These parameters are unbounded
            if isinstance(a, GamutUnbound):
                a = None
            if isinstance(b, GamutUnbound):
                b = None

            if (a is not None and value < (a - THRESHOLD)) or (b is not None and value > (b + THRESHOLD)):
                return False

        return True
