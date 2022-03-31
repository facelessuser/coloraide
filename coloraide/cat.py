"""Chromatic adaptation transforms."""
from . import util
from . import algebra as alg
from functools import lru_cache
from .types import Matrix, MutableMatrix, Vector, MutableVector
from typing import Tuple, Dict, cast

# From CIE 2004 Colorimetry T.3 and T.8
# B from https://en.wikipedia.org/wiki/Standard_illuminant#White_point
WHITES = {
    "2deg": {
        "A": (0.44758, 0.40745),
        "B": (0.34842, 0.35161),
        "C": (0.31006, 0.31616),
        "D50": (0.34570, 0.35850),  # Use 4 digits like everyone
        "D55": (0.33243, 0.34744),
        "D65": (0.31270, 0.32900),  # Use 4 digits like everyone
        "D75": (0.29903, 0.31488),
        "E": (1 / 3, 1 / 3),
        "F2": (0.37210, 0.37510),
        "F7": (0.31290, 0.32920),
        "F11": (0.38050, 0.37690)
    },

    "10deg": {
        "A": (0.45117, 0.40594),
        "B": (0.34980, 0.35270),
        "C": (0.31039, 0.31905),
        "D50": (0.34773, 0.35952),
        "D55": (0.33412, 0.34877),
        "D65": (0.31382, 0.33100),
        "D75": (0.29968, 0.31740),
        "E": (1 / 3, 1 / 3),
        "F2": (0.37925, 0.36733),
        "F3": (0.41761, 0.38324),
        "F11": (0.38541, 0.37123)
    }
}

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
    ],
    "cat16": [
        # https://arxiv.org/pdf/1802.06067.pdf
        [-0.401288, -0.250268, -0.002079],
        [0.650173, 1.204414, 0.048952],
        [-0.051461, -0.045854, -0.953127]
    ]
}  # type: Dict[str, Matrix]


@lru_cache(maxsize=20)
def calc_adaptation_matrices(
    w1: Tuple[float, float],
    w2: Tuple[float, float],
    method: str = 'bradford'
) -> Tuple[MutableMatrix, MutableMatrix]:
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
    mi = alg.inv(m)

    try:
        first = alg.dot(m, util.xy_to_xyz(w1), alg.A2D_A1D)
    except KeyError:  # pragma: no cover
        raise ValueError('Unknown white point encountered: {}'.format(w1))

    try:
        second = alg.dot(m, util.xy_to_xyz(w2), alg.A2D_A1D)
    except KeyError:  # pragma: no cover
        raise ValueError('Unknown white point encountered: {}'.format(w2))

    m2 = cast(MutableMatrix, alg.diag(cast(Vector, alg.divide(cast(Vector, first), cast(Vector, second), alg.A1D))))
    adapt = cast(MutableMatrix, alg.dot(mi, alg.dot(m2, m, alg.A2D), alg.A2D))

    return adapt, alg.inv(adapt)


def get_adaptation_matrix(w1: Tuple[float, float], w2: Tuple[float, float], method: str) -> MutableMatrix:
    """
    Get the appropriate matrix for chromatic adaptation.

    If the required matrices are not in the cache, they will be calculated.
    Since white points are sorted by name, regardless of the requested
    conversion direction, the same matrices will be retrieved from the cache.
    """

    a, b = sorted([w1, w2])
    m, mi = calc_adaptation_matrices(a, b, method)
    return mi if a != w2 else m


def chromatic_adaptation(
    w1: Tuple[float, float],
    w2: Tuple[float, float],
    xyz: Vector,
    method: str = 'bradford'
) -> MutableVector:
    """Chromatic adaptation."""

    if w1 == w2:
        # No adaptation is needed if the white points are identical.
        return list(xyz)
    else:
        # Get the appropriate chromatic adaptation matrix and apply.
        return cast(MutableVector, alg.dot(get_adaptation_matrix(w1, w2, method), xyz, alg.A2D_A1D))
