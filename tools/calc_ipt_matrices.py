"""
Calculate IPT matrices.

https://scholarworks.rit.edu/cgi/viewcontent.cgi?article=3862&context=theses
"""
import sys
import os

sys.path.insert(0, os.getcwd())

from tools.calc_xyz_transform import white_d65  # noqa: E402
from coloraide import algebra as alg  # noqa: E402

# IPT provides 2 matrices, the forward and reverse transform.
# These matrices are given at 16 bit accuracy. If the forward
# transform is used to generate the inverse matrix, LMS will
# never cleanly resolve to `[1, 1, 1]` for white. But if you
# use the reverse transform to generate the forward matrix,
# LMS will resolve to `[1, 1, 1]` with 64 bit accuracy.
# Because of this, we invert the reverse transform to get the
# forward transform for better double precision conversions.

# m1 = [
#     [0.4002, 0.7075, -0.0807],
#     [-0.2280, 1.1500, 0.0612],
#     [0.0, 0.0, 0.9184]
# ]

m1 = [
    [1.8502, -1.1383, 0.2385],
    [0.3668, 0.6439, -0.0107],
    [0.0, 0.0, 1.0889]
]

m2 = [
    [0.4000, 0.4000, 0.2000],
    [4.4550, -4.8510, 0.3960],
    [0.8056, 0.3572, -1.1628]
]

# IPT XYZ <-> LMS transform was originally created and optimized for the
# white point `[0.9504, 1.0, 1.0889]`, but our library uses `color(xyz-d65 0.95046 1 1.0891 / 1)`,
# but without rounding. While we could use the IPT white point, chromatically adapting ours
# to theirs, we've decided to just adapt the XYZ <-> LMS matrix. This could be done in two ways,
# combine the XYZ <-> LMS matrix with a Bradford adaptation matrix, or just adapt the matrix
# to yield an LMS of [1, 1, 1] when given our white point. Since the IPT matrices are
# only accurate up to 16 bit anyway and the white points are so close, the end result is
# comparable either way, both yielding the same IPT values up to 16 bit.
lms = alg.solve(m1, white_d65)
lms2xyz = alg.multiply(m1, lms)
xyz2lms = alg.inv(lms2xyz)


if __name__ == "__main__":
    print('===== XYZ to LMS =====')
    alg.pprint(xyz2lms)
    print('===== LMS to XYZ =====')
    alg.pprint(lms2xyz)
    print('===== LMS P to IPT =====')
    alg.pprint(m2)
    print('===== IPT to LMS P =====')
    alg.pprint(alg.inv(m2))
