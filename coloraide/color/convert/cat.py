"""Chromatic adaptation transforms."""
from ... import util
from ... spaces import WHITES
from functools import lru_cache

# Conversion matrices
CATS = {
    "bradford": [
        # http://brucelindbloom.com/Eqn_ChromAdapt.html
        # https://hrcak.srce.hr/file/95370
        [0.8951000, 0.2664000, -0.1614000],
        [-0.7502000, 1.7135000, 0.0367000],
        [0.0389000, -0.0685000, 1.0296000]
    ],
    "von-kries": [
        # http://brucelindbloom.com/Eqn_ChromAdapt.html
        # https://hrcak.srce.hr/file/95370
        [0.4002400, 0.7076000, -0.0808100],
        [-0.2263000, 1.1653200, 0.0457000],
        [0.0000000, 0.0000000, 0.9182200]
    ],
    "xyz-scaling": [
        # http://brucelindbloom.com/Eqn_ChromAdapt.html
        # https://hrcak.srce.hr/file/95370
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ],
    "cat02": [
        # https://en.wikipedia.org/wiki/CIECAM02#CAT02
        [0.7328000, 0.4296000, -0.1624000],
        [-0.7036000, 1.6975000, 0.0061000],
        [0.0030000, 0.0136000, 0.9834000]
    ],
    "cmccat97": [
        # https://hrcak.srce.hr/file/95370
        [0.8951000, -0.7502000, 0.0389000],
        [0.2664000, 1.7135000, 0.0685000],
        [-0.1614000, 0.0367000, 1.0296000],
    ],
    "sharp": [
        # https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.14.918&rep=rep1&type=pdf
        [1.2694000, -0.0988000, -0.1706000],
        [-0.8364000, 1.8006000, 0.0357000],
        [0.0297000, -0.0315000, 1.0018000]
    ],
    'cmccat2000': [
        # https://hrcak.srce.hr/file/95370
        # https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.14.918&rep=rep1&type=pdf
        [0.7982000, 0.3389000, -0.1371000],
        [-0.5918000, 1.5512000, 0.0406000],
        [0.0008000, 0.0239000, 0.9753000]
    ]
}


@lru_cache(maxsize=20)
def calc_adaptation_matrices(w1, w2, method='bradford'):
    """
    Get the von Kries based adaptation matrix based on the method and illuminants.

    Since these calculated matrices are cached, this greatly reduces
    performance hit as the initial matrices only have to be calculated
    once for a given pair of white points and CAT.

    Granted, we are currently, capped at 20 in the cache, but the average user
    isn't going to be swapping between over 20 methods and white points in a
    short period of time. We could always increase the cache if necessary.
    """

    try:
        m = CATS[method]
    except KeyError:  # pragma: no cover
        raise ValueError('Unknown chromatic adaptation method encountered: {}'.format(method))
    mi = util.inv(m)

    try:
        first = util.dot(m, WHITES[w1])
    except KeyError:  # pragma: no cover
        raise ValueError('Unknown white point encountered: {}'.format(w1))

    try:
        second = util.dot(m, WHITES[w2])
    except KeyError:  # pragma: no cover
        raise ValueError('Unknown white point encountered: {}'.format(w2))

    m2 = util.diag(util.divide(first, second))
    adapt = util.dot(mi, util.dot(m2, m))

    return adapt, util.inv(adapt)


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
