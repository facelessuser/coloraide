"""Calculate Jzazbz matrices."""
import sys
import os

sys.path.insert(0, os.getcwd())

from coloraide import algebra as alg  # noqa: E402

m1 = [
    [0.41478972, 0.579999, 0.0146480],
    [-0.2015100, 1.120649, 0.0531008],
    [-0.0166008, 0.264800, 0.6684799]
]

m2 = [
    [0.5, 0.5, 0],
    [3.524000, -4.066708, 0.542708],
    [0.199076, 1.096799, -1.295875]
]


if __name__ == "__main__":
    print('===== XYZ to LMS =====')
    alg.pprint(m1)
    print('===== LMS to XYZ =====')
    alg.pprint(alg.inv(m1))
    print('===== PQ LMS to Izazbz =====')
    alg.pprint(m2)
    print('===== Izazbz to PQ LMS =====')
    alg.pprint(alg.inv(m2))
