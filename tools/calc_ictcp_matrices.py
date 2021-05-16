"""
Calculate ICtCp matrices.

https://professional.dolby.com/siteassets/pdfs/ictcp_dolbywhitepaper_v071.pdf
"""
import numpy as np

np.set_printoptions(precision=None, sign='-', floatmode='unique')

a = np.asfarray(
    [
        [0.92, 0.04, 0.04],
        [0.04, 0.92, 0.04],
        [0.04, 0.04, 0.92]
    ]
)

b = np.asfarray(
    [
        [0.4002, 0.7076, -0.0808],
        [-0.2263, 1.1653, 0.0457],
        [0, 0, 0.9182]
    ]
)

# XYZ to LMS
m1 = np.dot(a, b)

# LMS to ICtCp
m2 = np.asfarray(
    [
        [2048 / 4096, 2048 / 4096, 0],
        [6610 / 4096, -13613 / 4096, 7003 / 4096],
        [17933 / 4096, -17390 / 4096, -543 / 4096]
    ]
)

if __name__ == "__main__":
    print('===== XYZ to LMS =====')
    print(m1)
    print('===== LMS to XYZ =====')
    print(np.linalg.inv(m1))
    print('===== PQ LMS to ICtCp =====')
    print(m2)
    print('===== ICtCp to PQ LMS =====')
    print(np.linalg.inv(m2))
