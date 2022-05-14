"""
Calculate `oklab` matrices.

https://github.com/w3c/csswg-drafts/issues/6642#issuecomment-945714988
"""
import sys
import os

sys.path.insert(0, os.getcwd())

import tools.calc_xyz_transform as xyzt  # noqa: E402
from coloraide import algebra as alg  # noqa: E402

# Calculated using our own `calc_xyz_transform.py`
RGB_TO_XYZ, XYZ_TO_RGB = xyzt.get_matrix(xyzt.white_d65, 'srgb')

M0 = [
    [0.77849780, 0.34399940, -0.12249720],
    [0.03303601, 0.93076195, 0.03620204],
    [0.05092917, 0.27933344, 0.66973739]
]

XYZ_TO_LMS = alg.divide(M0, alg.outer(alg.dot(M0, xyzt.white_d65), alg.ones(3)))
LMS_TO_XYZ = alg.inv(XYZ_TO_LMS)

SRGBL_TO_LMS = alg.dot(XYZ_TO_LMS, RGB_TO_XYZ)
LMS_TO_SRGBL = alg.inv(SRGBL_TO_LMS)


LMS3_TO_OKLAB = [
    [0.2104542553, 0.793617785, -0.0040720468],
    [1.9779984951, -2.428592205, 0.4505937099],
    [0.0259040371, 0.7827717662, -0.808675766]
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
        print(v, end='')
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
