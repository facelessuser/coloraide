"""
Calculate ICtCp matrices.

https://professional.dolby.com/siteassets/pdfs/ictcp_dolbywhitepaper_v071.pdf
"""
import sys
import os

sys.path.insert(0, os.getcwd())

from coloraide import algebra as alg  # noqa: E402


a = [
    [0.92, 0.04, 0.04],
    [0.04, 0.92, 0.04],
    [0.04, 0.04, 0.92]
]

b = [
    [0.4002, 0.7076, -0.0808],
    [-0.2263, 1.1653, 0.0457],
    [0, 0, 0.9182]
]

# XYZ to LMS
m1 = alg.matmul(a, b)

# LMS to ICtCp
m2 = [
    [2048, 2048, 0],
    [6610, -13613, 7003],
    [17933, -17390, -543]
]

m2 = alg.divide(m2, 4096)


if __name__ == "__main__":
    print('===== XYZ to LMS =====')
    alg.pprint(m1)
    print('===== LMS to XYZ =====')
    alg.pprint(alg.inv(m1))
    print('===== PQ LMS to ICtCp =====')
    alg.pprint(m2)
    print('===== ICtCp to PQ LMS =====')
    alg.pprint(alg.inv(m2))
