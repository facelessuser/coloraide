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
m1 = alg.dot(a, b)

# LMS to ICtCp
m2 = [
    [2048, 2048, 0],
    [6610, -13613, 7003],
    [17933, -17390, -543]
]

m2 = alg.divide(m2, 4096)


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
    print('===== XYZ to LMS =====')
    pprint(m1)
    print('===== LMS to XYZ =====')
    pprint(alg.inv(m1))
    print('===== PQ LMS to ICtCp =====')
    pprint(m2)
    print('===== ICtCp to PQ LMS =====')
    pprint(alg.inv(m2))
