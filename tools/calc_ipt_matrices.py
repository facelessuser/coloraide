"""
Calculate IPT matrices.

https://scholarworks.rit.edu/cgi/viewcontent.cgi?article=3862&context=theses
"""
import sys
import os

sys.path.insert(0, os.getcwd())

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


if __name__ == "__main__":
    print('===== XYZ to LMS =====')
    alg.pprint(alg.inv(m1))
    print('===== LMS to XYZ =====')
    alg.pprint(m1)
    print('===== LMS P to IPT =====')
    alg.pprint(m2)
    print('===== IPT to LMS P =====')
    alg.pprint(alg.inv(m2))
