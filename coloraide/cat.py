"""Chromatic adaptation transforms."""
from __future__ import annotations
from . import util
from abc import ABCMeta, abstractmethod
from . import algebra as alg
import functools
from .types import Matrix, VectorLike, Vector, Plugin
from typing import Any  # noqa: F401

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


def calc_adaptation_matrices(
    w1: tuple[float, float],
    w2: tuple[float, float],
    m: Matrix,
) -> tuple[Matrix, Matrix]:
    """
    Get the von Kries based adaptation matrix based on the method and illuminants.

    Since these calculated matrices are cached, this greatly reduces
    performance hit as the initial matrices only have to be calculated
    once for a given pair of white points and CAT.

    Granted, we are currently, capped at 20 in the cache, but the average user
    isn't going to be swapping between over 20 methods and white points in a
    short period of time. We could always increase the cache if necessary.
    """

    first = alg.dot(m, util.xy_to_xyz(w1), dims=alg.D2_D1)
    second = alg.dot(m, util.xy_to_xyz(w2), dims=alg.D2_D1)
    m2 = alg.diag(alg.divide(first, second, dims=alg.D1))
    adapt = alg.multi_dot([alg.inv(m), m2, m])  # type: Any

    return adapt, alg.inv(adapt)


class CAT(Plugin, metaclass=ABCMeta):
    """Chromatic adaptation."""

    NAME = ''

    @abstractmethod
    def adapt(self, w1: tuple[float, float], w2: tuple[float, float], xyz: VectorLike) -> Vector:
        """Adapt a given XYZ color using the provided white points."""


class VonKries(CAT):
    """
    Von Kries CAT.

    http://brucelindbloom.com/Eqn_ChromAdapt.html
    https://hrcak.srce.hr/file/95370
    """

    NAME = 'von-kries'

    MATRIX = [
        [0.4002400, 0.7076000, -0.0808100],
        [-0.2263000, 1.1653200, 0.0457000],
        [0.0000000, 0.0000000, 0.9182200]
    ]  # type: Matrix

    @classmethod
    @functools.lru_cache(maxsize=20)
    def get_adaptation_matrices(
        cls: type[VonKries],
        w1: tuple[float, float],
        w2: tuple[float, float]
    ) -> tuple[Matrix, Matrix]:
        """Get the adaptation matrices."""

        return calc_adaptation_matrices(w1, w2, cls.MATRIX)

    def adapt(self, w1: tuple[float, float], w2: tuple[float, float], xyz: VectorLike) -> Vector:
        """Adapt a given XYZ color using the provided white points."""

        # We are already using the correct white point
        if w1 == w2:
            return list(xyz)

        a, b = sorted([w1, w2])
        m, mi = self.get_adaptation_matrices(a, b)
        return alg.dot(mi if a != w2 else m, xyz, dims=alg.D2_D1)


class Bradford(VonKries):
    """
    Bradford CAT.

    http://brucelindbloom.com/Eqn_ChromAdapt.html
    https://hrcak.srce.hr/file/95370
    """

    NAME = "bradford"

    MATRIX = [
        [0.8951000, 0.2664000, -0.1614000],
        [-0.7502000, 1.7135000, 0.0367000],
        [0.0389000, -0.0685000, 1.0296000]
    ]


class XYZScaling(VonKries):
    """
    XYZ Scaling CAT.

    http://brucelindbloom.com/Eqn_ChromAdapt.html
    https://hrcak.srce.hr/file/95370
    """

    NAME = "xyz-scaling"

    MATRIX = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]


class CAT02(VonKries):
    """
    CAT02 CAT.

    https://en.wikipedia.org/wiki/CIECAM02#CAT02
    """

    NAME = "cat02"

    MATRIX = [
        [0.7328000, 0.4296000, -0.1624000],
        [-0.7036000, 1.6975000, 0.0061000],
        [0.0030000, 0.0136000, 0.9834000]
    ]


class CMCCAT97(VonKries):
    """
    CMCCAT97 CAT.

    https://hrcak.srce.hr/file/95370
    """

    NAME = "cmccat97"

    MATRIX = [
        [0.8951000, -0.7502000, 0.0389000],
        [0.2664000, 1.7135000, 0.0685000],
        [-0.1614000, 0.0367000, 1.0296000],
    ]


class Sharp(VonKries):
    """
    Sharp CAT.

    https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.14.918&rep=rep1&type=pdf
    """

    NAME = "sharp"

    MATRIX = [
        [1.2694000, -0.0988000, -0.1706000],
        [-0.8364000, 1.8006000, 0.0357000],
        [0.0297000, -0.0315000, 1.0018000]
    ]


class CMCCAT2000(VonKries):
    """
    CMCCAT2000 CAT.

    https://hrcak.srce.hr/file/95370
    https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.14.918&rep=rep1&type=pdf
    """

    NAME = 'cmccat2000'

    MATRIX = [
        [0.7982000, 0.3389000, -0.1371000],
        [-0.5918000, 1.5512000, 0.0406000],
        [0.0008000, 0.0239000, 0.9753000]
    ]


class CAT16(VonKries):
    """
    CAT16 CAT.

    https://arxiv.org/pdf/1802.06067.pdf
    """

    NAME = "cat16"

    MATRIX = [
        [0.401288, 0.650173, -0.051461],
        [-0.250268, 1.204414, 0.045854],
        [-0.002079, 0.048952, 0.953127]
    ]
