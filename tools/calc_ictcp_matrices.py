"""
Calculate ICtCp matrices.

https://professional.dolby.com/siteassets/pdfs/ictcp_dolbywhitepaper_v071.pdf
"""
import sys
import os

sys.path.insert(0, os.getcwd())

from coloraide import algebra as alg  # noqa: E402
import tools.calc_xyz_transform as xyzt  # noqa: E402


RGB_TO_XYZ, XYZ_TO_RGB = xyzt.get_matrix(xyzt.white_d65, 'rec2020')

# Use rational values and apply Rec. 2020 matrix to get a precise XYZ to LMS matrix
m1 = [
    [1688, 2146, 262],
    [683, 2951, 462],
    [99, 309, 3688]
]
m1 = alg.matmul(alg.divide(m1, 4096), XYZ_TO_RGB)

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
