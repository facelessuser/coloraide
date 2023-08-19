"""
Calculate IgPgTg matrices.

https://www.ingentaconnect.com/content/ist/jpi/2020/00000003/00000002/art00002#
"""
import sys
import os

sys.path.insert(0, os.getcwd())

from coloraide import algebra as alg  # noqa: E402

m1 = [
    [2.968, 2.741, -0.649],
    [1.237, 5.969, -0.173],
    [-0.318, 0.387, 2.311]
]

m2 = [
    [0.117, 1.464, 0.130],
    [8.285, -8.361, 21.40],
    [-1.208, 2.412, -36.53]
]


if __name__ == "__main__":
    print('===== XYZ to LMS =====')
    alg.pprint(m1)
    print('===== LMS to XYZ =====')
    alg.pprint(alg.inv(m1))
    print('===== LMS to IgPgTg =====')
    alg.pprint(m2)
    print('===== IgPgTg to LMS =====')
    alg.pprint(alg.inv(m2))
