"""
Calculate IPT matrices.

https://scholarworks.rit.edu/cgi/viewcontent.cgi?article=3862&context=theses
"""
import sys
import os

sys.path.insert(0, os.getcwd())

from coloraide import algebra as alg  # noqa: E402

m1 = [
    [0.4002, 0.7075, -0.0807],
    [-0.2280, 1.1500, 0.0612],
    [0.0, 0.0, 0.9184]
]

m2 = [
    [0.4000, 0.4000, 0.2000],
    [4.4550, -4.8510, 0.3960],
    [0.8056, 0.3572, -1.1628]
]


if __name__ == "__main__":
    print('===== XYZ to LMS =====')
    alg.pprint(m1)
    print('===== LMS to XYZ =====')
    alg.pprint(alg.inv(m1))
    print('===== LMS P to IPT =====')
    alg.pprint(m2)
    print('===== IPT to LMS P =====')
    alg.pprint(alg.inv(m2))
