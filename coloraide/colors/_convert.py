"""Convert utilities."""
from .. import util

x = 0.3127
y = 0.3290
z = 0.3583
white_d65 = [x / y, y / y, z / y]

x = 0.3457
y = 0.3585
z = 0.2958
white_d50 = [x / y, y / y, z / y]

WHITES = {
    "D50": white_d50,
    "D65": white_d65
}


def d50_to_d65(xyz):
    """Bradford chromatic adaptation from D50 to D65."""

    m = [
        [0.9554734214880751, -0.0230984549487647, 0.0632592432005707],
        [-0.0283697093338638, 1.0099953980813041, 0.0210414411919173],
        [0.0123140148644820, -0.0205076492988990, 1.3303659262421237]
    ]

    return util.dot(m, xyz)


def d65_to_d50(xyz):
    """Bradford chromatic adaptation from D65 to D50."""

    m = [
        [1.0479297925449969, 0.0229468706016097, -0.0501922662892052],
        [0.0296278087700559, 0.9904344267538799, -0.0170737990634188],
        [-0.0092430406462045, 0.0150551914902981, 0.7518742814281371]
    ]

    return util.dot(m, xyz)


class Convert:
    """Convert class."""

    @classmethod
    def _constrain_hue(cls, hue):
        """Constrain hue to 0 - 360."""

        return hue % 360 if not util.is_nan(hue) else hue

    @classmethod
    def _chromatic_adaption(cls, w1, w2, xyz):
        """Chromatic adaption."""

        if w1 == w2:
            return xyz
        elif w1 == WHITES["D50"] and w2 == WHITES["D65"]:
            return d50_to_d65(xyz)
        elif w1 == WHITES["D65"] and w2 == WHITES["D50"]:
            return d65_to_d50(xyz)
        else:  # pragma: no cover
            # Should only occur internally if we are doing something wrong.
            raise ValueError('Unknown white point encountered: {} -> {}'.format(str(w1), str(w2)))

    def convert(self, space, *, fit=False):
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

        obj = self.parent.CS_MAP.get(space)
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))

        # See if there is a direct conversion route
        func = None
        coords = self._coords
        if hasattr(self, convert_to):
            func = getattr(self, convert_to)
            coords = func(coords)
        elif hasattr(obj, convert_from):
            func = getattr(obj, convert_from)
            coords = func(coords)

        # See if there is an XYZ route
        if func is None and self.space() != space:
            func = getattr(self, '_to_xyz')
            coords = func(coords)

            if space != 'xyz':
                func = getattr(obj, '_from_xyz')
                coords = func(coords)

        result = obj(coords, self.alpha)
        result.parent = self.parent

        return result
