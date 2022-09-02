"""
Calculate `oklab` matrices.

https://github.com/w3c/csswg-drafts/issues/6642#issuecomment-945714988
"""
from fractions import Fraction
import sys
import os

sys.path.insert(0, os.getcwd())

import tools.falgebra as alg  # noqa: E402
import tools.calc_xyz_transform as xyzt  # noqa: E402

# Calculated using our own `calc_xyz_transform.py`
RGB_TO_XYZ, XYZ_TO_RGB = xyzt.get_matrix(xyzt.white_d65, 'srgb')

M0 = [
    [Fraction(77849780, 100000000), Fraction(34399940, 100000000), Fraction(-12249720, 100000000)],
    [Fraction(3303601, 100000000), Fraction(93076195, 100000000), Fraction(3620204, 100000000)],
    [Fraction(5092917, 100000000), Fraction(27933344, 100000000), Fraction(66973739, 100000000)]
]

XYZ_TO_LMS = alg.divide(M0, alg.outer(alg.dot(M0, xyzt.white_d65), alg.ones(3)))
LMS_TO_XYZ = alg.inv(XYZ_TO_LMS)

SRGBL_TO_LMS = alg.dot(XYZ_TO_LMS, RGB_TO_XYZ)
LMS_TO_SRGBL = alg.inv(SRGBL_TO_LMS)


LMS3_TO_OKLAB = [
    [Fraction(2104542553, 10000000000), Fraction(7936177850, 10000000000), Fraction(-40720468, 10000000000)],
    [Fraction(19779984951, 10000000000), Fraction(-24285922050, 10000000000), Fraction(4505937099, 10000000000)],
    [Fraction(259040371, 10000000000), Fraction(7827717662, 10000000000), Fraction(-8086757660, 10000000000)]
]

OKLAB_TO_LMS3 = alg.inv(LMS3_TO_OKLAB)


def pprint(value):
    """Print the matrix."""
    print('[', end='')
    first = True
    for v in value:
        if first:
            first = False
        else:
            print(',\n ', end='')
        if isinstance(v, Fraction):
            print(v.numerator / v.denominator, end='')
        else:
            print([c.numerator / c.denominator if isinstance(c, Fraction) else c for c in v], end='')
    print(']')


if __name__ == "__main__":
    print('===== sRGB Linear -> lms =====')
    pprint(SRGBL_TO_LMS)
    print('===== lms -> sRGB Linear =====')
    pprint(LMS_TO_SRGBL)
    print('===== XYZ D65 Linear -> lms =====')
    pprint(XYZ_TO_LMS)
    print('===== lms -> XYZ D65 =====')
    pprint(LMS_TO_XYZ)
    print('===== lms ** 1/3 -> Oklab =====')
    pprint(LMS3_TO_OKLAB)
    print('===== Oklab -> lms ** 1/3 =====')
    pprint(OKLAB_TO_LMS3)
