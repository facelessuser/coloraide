"""Gamut handling."""
from .. import util

THRESHOLD = 0.000075


class GamutHue(float):
    """Gamut hue."""


class GamutBound(float):
    """Bounded gamut value."""


class GamutUnbound(float):
    """Unbounded gamut value."""


def lch_chroma(base, color):
    """
    Gamut mapping via chroma LCH.

    Algorithm comes from https://colorjs.io/docs/gamut-mapping.html.

    The idea is to hold hue and lightness constant and decrease lightness until
    color comes under gamut.

    We'll use a binary search and at after each stage, we will clip the color
    and compare the distance of the two colors (clipped and current color via binary search).
    If the distance is less than two, we can return the clipped color.

    ---
    Original Authors: Lea Verou, Chris Lilley
    License: MIT (As noted in https://github.com/LeaVerou/color.js/blob/master/package.json)
    """

    space = color.space()
    clipped = base.clone()
    clipped.fit_gamut(space=space, method="clip")
    base_error = base.delta(clipped)

    if base_error > 2.3:
        mapcolor = color.convert("lch")
        threshold = .001
        low = 0.0
        high = mapcolor.chroma
        error = color.delta(clipped)

        while (high - low) > threshold and error < base_error:
            clipped = mapcolor.clone()
            clipped.fit_gamut(space, method="clip")
            delta = mapcolor.delta(clipped)
            error = color.delta(mapcolor)
            if delta - 2 < threshold:
                low = mapcolor.chroma
            else:
                if abs(delta - 2) < threshold:
                    break
                high = mapcolor.chroma
            mapcolor.chroma = (high + low) / 2
        mapcolor.fit_gamut(space, method="clip")
        color.mutate(mapcolor)
    else:
        color.mutate(clipped)
    return color._channels


def gamut_clip(base, color):
    """Gamut clipping."""

    channels = color._channels
    gamut = color._gamut
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

    def fit_gamut(self, space=None, method="lch-chroma"):
        """Fit the gamut using the provided method."""

        if method == "clip":
            func = gamut_clip
        elif method == "lch-chroma":
            func = lch_chroma

        if space is not None:
            c = self.convert(space)
        else:
            c = self.clone()

        fit = func(self, c)
        for i in range(len(fit)):
            c._channels[i] = fit[i]
        self.mutate(c)
        self._on_convert()

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
