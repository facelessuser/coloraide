"""Convert utilities."""
from .. import util


class Convert:
    """Conversion methods."""

    def convert(self, space, *, fit=False, in_place=False):
        """Convert to color space."""

        space = space.lower()

        if fit:
            method = None if not isinstance(fit, str) else fit
            if not self.in_gamut(space, tolerance=0.0):
                clone = self.clone()
                result = clone.convert(space)
                result.fit(space, method=method, in_place=True)
                return result

        convert_to = '_to_{}'.format(space)
        convert_from = '_from_{}'.format(self.space())

        obj = self.CS_MAP.get(space)
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))

        # See if there is a direct conversion route
        func = None
        coords = self.coords()
        if hasattr(self._space, convert_to):
            func = getattr(self._space, convert_to)
            coords = func(coords)
        elif hasattr(obj, convert_from):
            func = getattr(obj, convert_from)
            coords = func(coords)

        # See if there is an XYZ route
        if func is None and self.space() != space:
            func = getattr(self._space, '_to_xyz')
            coords = func(coords)

            if space != 'xyz':
                func = getattr(obj, '_from_xyz')
                coords = func(coords)

        converted = self.new(space, coords, self.alpha)
        return self.mutate(converted) if in_place else converted

    def mutate(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
        """Mutate the current color to a new color."""

        self._attach(self._parse(color, data, alpha, filters=filters, **kwargs))
        return self

    def update(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
        """Update the existing color space with the provided color."""

        clone = self.clone()
        obj = self._parse(color, data, alpha, filters=filters, **kwargs)
        clone._attach(obj)

        if clone.space() != self.space():
            clone.convert(self.space(), in_place=True)

        self._attach(clone._space)
        clone._space = False
        return self
