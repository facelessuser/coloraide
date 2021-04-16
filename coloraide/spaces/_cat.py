"""Chromatic adaption transforms."""
from .. import util

white_d65 = [0.95047, 1.00000, 1.08883]
white_d50 = [0.96422, 1.00000, 0.82521]

WHITES = {
    "D50": white_d50,
    "D65": white_d65
}


def d50_to_d65(xyz):
    """Bradford chromatic adaptation from D50 to D65."""

    m = [
        [0.9555766150331048, -0.0230393447160789, 0.0631636322498012],
        [-0.0282895442435549, 1.0099416173711144, 0.0210076549961903],
        [0.0122981657172073, -0.0204830252324494, 1.3299098264497566]
    ]

    return util.dot(m, xyz)


def d65_to_d50(xyz):
    """Bradford chromatic adaptation from D65 to D50."""

    m = [
        [1.0478112436606313, 0.022886602481693, -0.0501269759685289],
        [0.0295423982905749, 0.9904844034904393, -0.0170490956289616],
        [-0.0092344897233095, 0.0150436167934987, 0.752131635474606]
    ]

    return util.dot(m, xyz)


def chromatic_adaption(w1, w2, xyz):
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
