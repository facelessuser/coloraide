"""Gamut handling."""
from ... import util
from ... spaces import Angle, GamutBound
from . import clip
from . import lch_chroma


def norm_angles(color):
    """Normalize angles."""

    channels = util.no_nan(color.coords())
    gamut = color._space.RANGE
    fit = []
    for i, value in enumerate(channels):
        a = gamut[i][0]

        # Wrap the angle
        if isinstance(a, Angle):
            fit.append(value % 360.0)
            continue

        # Fit value in bounds.
        fit.append(value)
    return fit


class Gamut:
    """Handle gamut related functions."""

    def fit(self, space=None, *, method=None, in_place=False):
        """Fit the gamut using the provided method."""

        if space is None:
            space = self.space()

        if method is None:
            method = self.FIT

        this = self.clone() if not in_place else self

        # Select appropriate mapping algorithm
        if method == "clip":
            func = clip.fit
        elif method == "lch-chroma":
            func = lch_chroma.fit
        else:
            # Unknown fit method
            raise ValueError("'{}' gamut mapping is not currently supported".format(method))

        # Convert to desired space
        c = self.convert(space)

        # If we are perfectly in gamut, don't waste time fitting, just normalize hues.
        # If out of gamut, apply mapping/clipping/etc.
        c._space._coords, c._space._alpha = (
            c._space.null_adjust(norm_angles(c) if c.in_gamut(tolerance=0.0) else func(c), self.alpha)
        )

        # Adjust "this" color
        return this.update(c)

    def in_gamut(self, space=None, *, tolerance=util.DEF_FIT_TOLERANCE):
        """Check if current color is in gamut."""

        space = space.lower() if space is not None else self.space()

        # Check gamut in the provided space
        if space is not None and space != self.space():
            c = self.convert(space)
            return c.in_gamut(tolerance=tolerance)

        # Check the color space specified for gamut checking.
        # If it proves to be in gamut, we will then test if the current
        # space is constrained properly.
        if self._space.GAMUT_CHECK is not None:
            c = self.convert(self._space.GAMUT_CHECK)
            if not c.in_gamut(tolerance=tolerance):
                return False

        # Verify the values are in bound
        channels = util.no_nan(self.coords())
        for i, value in enumerate(channels):
            a, b = self._space.RANGE[i]
            is_bound = isinstance(self._space.RANGE[i], GamutBound)

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
