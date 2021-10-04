"""Convert utilities."""
from ... import util
from . import cat


class Convert:
    """Conversion methods."""

    def chromatic_adaptation(self, w1, w2, xyz):
        """Apply chromatic adaption to XYZ coordinates."""

        method = self.CHROMATIC_ADAPTATION
        return cat.chromatic_adaptation(w1, w2, xyz, method=method)

    def convert(self, space, *, fit=False, in_place=False):
        """Convert to color space."""

        space = space.lower()

        if fit:
            method = None if not isinstance(fit, str) else fit
            if not self.in_gamut(space, tolerance=0.0):
                converted = self.convert(space, in_place=in_place)
                return converted.fit(space, method=method, in_place=True)

        if self.space() != space:
            convert_to = '_to_{}'.format(space)
            convert_from = '_from_{}'.format(self.space())

            obj = self.CS_MAP.get(space)
            if obj is None:
                raise ValueError("'{}' is not a valid color space".format(space))

            # See if there is a direct conversion route
            func = None
            # Don't send NaNs
            coords = util.no_nan(self.coords())
            if hasattr(self._space, convert_to):
                func = getattr(self._space, convert_to)
                coords = func(self, coords)
            elif hasattr(obj, convert_from):
                func = getattr(obj, convert_from)
                coords = func(self, coords)

            # See if there is an XYZ route
            if func is None and self.space() != space:
                func = getattr(self._space, '_to_xyz')
                coords = func(self, coords)

                if space != 'xyz':
                    func = getattr(obj, '_from_xyz')
                    coords = func(self, coords)
        else:
            # Nothing to convert, just pass values as is
            coords = self.coords()

        return self.mutate(space, coords, self.alpha) if in_place else self.new(space, coords, self.alpha)

    def mutate(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
        """Mutate the current color to a new color."""

        c = self._parse(color, data=data, alpha=alpha, filters=filters, **kwargs)
        self._attach(c)
        return self

    def update(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
        """Update the existing color space with the provided color."""

        c = self._parse(color, data=data, alpha=alpha, filters=filters, **kwargs)
        space = self.space()
        self._attach(c)
        if c.space() != space:
            self.convert(space, in_place=True)
        return self
