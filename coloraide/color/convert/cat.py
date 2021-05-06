"""Chromatic adaptation transforms."""
from ... import util
from ... spaces import WHITES
from functools import lru_cache

# Conversion matrices: M and M^-1.
CATS = {
    "bradford": [
        [
            [0.8951000, 0.2664000, -0.1614000],
            [-0.7502000, 1.7135000, 0.0367000],
            [0.0389000, -0.0685000, 1.0296000]
        ],
        [
            [0.9869929054667121, -0.1470542564209901, 0.1599626516637312],
            [0.4323052697233944, 0.5183602715367774, 0.0492912282128556],
            [-0.0085286645751773, 0.0400428216540849, 0.96848669578755]
        ]
    ],
    "von-kries": [
        [
            [0.4002400, 0.7076000, -0.0808100],
            [-0.2263000, 1.1653200, 0.0457000],
            [0.0000000, 0.0000000, 0.9182200]
        ],
        [
            [1.8599363874558399e+00, -1.1293816185800916e+00, 2.1989740959619331e-01],
            [3.6119143624176753e-01, 6.3881246328504215e-01, -6.3705968386498990e-06],
            [0.0000000000000000e+00, 0.0000000000000000e+00, 1.0890636230968613e+00]
        ]
    ]
}


@lru_cache(maxsize=22)
def calc_adaptation_matrices(w1, w2, method='bradford'):
    """
    Get the adaptation matrix based on the method and illuminants.

    Since these calculated matrices are cached, this greatly reduces
    performance hit as the initial matrices only have to be calculated
    once for a given pair of white points and CAT.
    """

    try:
        m, mi = CATS[method]
    except KeyError:  # pragma: no cover
        raise ValueError('Unknown chromatic adaptation method encountered: {}'.format(method))

    try:
        first = util.dot(m, [[c] for c in WHITES[w1]])
    except KeyError:  # pragma: no cover
        raise ValueError('Unknown white point encountered: {}'.format(w1))

    try:
        second = util.dot(m, [[c] for c in WHITES[w2]])
    except KeyError:  # pragma: no cover
        raise ValueError('Unknown white point encountered: {}'.format(w2))

    m2 = util.divide(first, second)

    m3 = [
        [m2[0][0], 0, 0],
        [0, m2[1][0], 0],
        [0, 0, m2[2][0]]
    ]

    adapt = util.dot(mi, util.dot(m3, m))
    adapt_i = util.inv(adapt)

    return adapt, adapt_i


def get_adaptation_matrix(w1, w2, method):
    """
    Get the appropriate matrix for chromatic adaptation.

    If the required matrices are not in the cache, they will be calculated.
    Since white points are sorted by name, regardless of the requested
    conversion direction, the same matrices will be retrieved from the cache.
    """

    a, b = sorted([w1, w2])
    m, mi = calc_adaptation_matrices(a, b, method)
    return mi if a != w2 else m


def chromatic_adaptation(w1, w2, xyz, method='bradford'):
    """Chromatic adaptation."""

    if w1 == w2:
        # No adaptation is needed if the white points are identical.
        return xyz
    else:
        # Get the appropriate chromatic adaptation matrix and apply.
        return util.dot(get_adaptation_matrix(w1, w2, method), xyz)
