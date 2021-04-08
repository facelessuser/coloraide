"""Calculate Bradford CAT."""
import numpy as np

np.set_printoptions(precision=16, suppress=True, sign='-', floatmode='maxprec_equal')

x = 0.3127
y = 0.3290
z = 0.3583
white_d65 = [x / y, y / y, z / y]

x = 0.3457
y = 0.3585
z = 0.2958
white_d50 = [x / y, y / y, z / y]

m = [
    [0.8951, 0.2664, -0.1614],
    [-0.7502, 1.7135, 0.0367],
    [0.0389, -0.0685, 1.0296]
]
mi = np.linalg.inv(m)

wd50 = np.array(white_d50).reshape(3, 1)
wd65 = np.array(white_d65).reshape(3, 1)


def calculate_bradford_cat(src_white, dest_white):
    """Calculate Bradford CAT."""

    src = np.dot(m, src_white)
    dest = np.dot(m, dest_white)
    m2 = np.divide(dest, src)

    m3 = [
        [m2[0][0], 0, 0],
        [0, m2[1][0], 0],
        [0, 0, m2[2][0]]
    ]
    to_d50 = np.dot(mi, np.dot(m3, m))
    to_d65 = np.linalg.inv(to_d50)
    return to_d65, to_d50


if __name__ == '__main__':
    to_d65, to_d50 = calculate_bradford_cat(wd65, wd50)

    print('===== To D65 =====')
    print(to_d65)

    print('===== To D50 =====')
    print(to_d50)
