"""
RLAB.

https://scholarworks.rit.edu/cgi/viewcontent.cgi?article=1153&context=article
https://www.imaging.org/site/PDFS/Papers/1997/RP-0-67/2368.pdf

There was some conflicting info between the two papers. One cited M one way, and one cited the inverse.
One was clearly a mistake. It seems that the `imaging.org` one is the correct M. We ended up implementing
the "Refinement of the RLAB Color Space" algorithm and just replaced M with the correct one.

We did recalculate R for our white point to get a nice, clean transform.
"""

import sys
import os

sys.path.insert(0, os.getcwd())

from coloraide import algebra as alg  # noqa: E402
from coloraide import util  # noqa: E402
from coloraide.cat import WHITES  # noqa: E402


white_d65 = util.xy_to_xyz((0.31270, 0.32900))

R = [
    [1.9569, -1.1882, 0.2313],
    [0.3612, 0.6388, 0.0],
    [0.0, 0.0, 1.0000]
]

M = [
    [0.4002, 0.7076, -0.0808],
    [-0.2263, 1.1653, 0.0457],
    [0.0, 0.0, 0.9182]
]

YN = 318.0  # D65 `318 cd / m^2`
D = 0.0


def calc_a_lms(lms):
    """Calculate the various matrix diagonal values."""

    a = []
    s = sum(lms)
    for c in lms:
        l = (3.0 * c) / s
        p = (1.0 + alg.nth_root(YN, 3) + l) / (1.0 + alg.nth_root(YN, 3) + 1.0 / l)
        a.append((p + D * (1.0 - p)) / c)
    return a


def calc_ram(white):
    """Calculate RAM."""

    xyz_w = util.xy_to_xyz(white)
    lms = alg.dot(M, xyz_w)
    a_lms = calc_a_lms(lms)
    A = alg.diag(a_lms)
    R = alg.multi_dot([alg.inv(alg.diag(xyz_w)), alg.inv(M), alg.inv(A)])
    ram = alg.dot(R, alg.dot(A, M))
    return ram


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
    RAM = calc_ram(WHITES['2deg']['D65'])
    print('===== XYZ to XYZref =====')
    pprint(RAM)
    print('===== XYZref to XYZ =====')
    pprint(alg.inv(RAM))
