"""Convert utilities."""
from .. import util

WHITES = {
    "D50": [0.96422, 1.00000, 0.82521],
    "D65": [0.95047, 1.00000, 1.08883]
}


def d50_to_d65(xyz):
    """Bradford chromatic adaptation from D50 to D65."""

    m = [
        [0.9555766, -0.0230393, 0.0631636],
        [-0.0282895, 1.0099416, 0.0210077],
        [0.0122982, -0.0204830, 1.3299098]
    ]

    return util.dot(m, xyz)


def d65_to_d50(xyz):
    """
    Bradford chromatic adaptation from D65 to D50.

    The matrix below is the result of three operations:
    - convert from XYZ to retinal cone domain
    - scale components from one reference white to another
    - convert back to XYZ
    http://www.brucelindbloom.com/index.html?Eqn_ChromAdapt.html
    """

    m = [
        [1.0478112, 0.0228866, -0.0501270],
        [0.0295424, 0.9904844, -0.0170491],
        [-0.0092345, 0.0150436, 0.7521316]
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
