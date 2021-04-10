"""Calculate XYZ conversion matrices."""
import numpy as np

np.set_printoptions(precision=16, sign='-')

white_d65 = [0.95047, 1.00000, 1.08883]
white_d50 = [0.96422, 1.00000, 0.82521]


def get_matrix(wp, space):
    """Get the matrices for the specified space."""

    if space == 'srgb':
        xr = 0.64
        yr = 0.33
        xg = 0.30
        yg = 0.60
        xb = 0.15
        yb = 0.06
    elif space == 'display-p3':
        xr = 0.68
        yr = 0.32
        xg = 0.265
        yg = 0.69
        xb = 0.150
        yb = 0.060
    elif space == 'rec2020':
        xr = 0.708
        yr = 0.292
        xg = 0.17
        yg = 0.797
        xb = 0.131
        yb = 0.046
    elif space == 'a98-rgb':
        xr = 0.64
        yr = 0.33
        xg = 0.21
        yg = 0.71
        xb = 0.15
        yb = 0.06
    elif space == 'prophoto-rgb':
        xr = 0.7347
        yr = 0.2653
        xg = 0.1596
        yg = 0.8404
        xb = 0.0366
        yb = 0.0001
    else:
        raise ValueError

    m = [
        [xr / yr, 1.0, (1.0 - xr - yr) / yr],
        [xg / yg, 1.0, (1.0 - xg - yg) / yg],
        [xb / yb, 1.0, (1.0 - xb - yb) / yb]
    ]
    mi = np.linalg.inv(m)

    rgb = np.dot(wp, mi).reshape(3, 1)
    rgb2xyz = np.multiply(rgb, m).transpose()
    xyz2rgb = np.linalg.inv(rgb2xyz)

    return rgb2xyz, xyz2rgb


if __name__ == "__main__":
    print('===== sRGB =====')
    to_xyz, from_xyz = get_matrix(white_d65, 'srgb')
    print('--- rgb -> xyz ---')
    print(to_xyz)
    print('--- xyz -> rgb ---')
    print(from_xyz)

    print('===== Display P3 =====')
    to_xyz, from_xyz = get_matrix(white_d65, 'display-p3')
    print('--- rgb -> xyz ---')
    print(to_xyz)
    print('--- xyz -> rgb ---')
    print(from_xyz)

    print('===== Adobe 98 =====')
    to_xyz, from_xyz = get_matrix(white_d65, 'a98-rgb')
    print('--- rgb -> xyz ---')
    print(to_xyz)
    print('--- xyz -> rgb ---')
    print(from_xyz)

    print('===== Rec.2020 =====')
    to_xyz, from_xyz = get_matrix(white_d65, 'rec2020')
    print('--- rgb -> xyz ---')
    print(to_xyz)
    print('--- xyz -> rgb ---')
    print(from_xyz)

    print('===== ProPhoto =====')
    to_xyz, from_xyz = get_matrix(white_d50, 'prophoto-rgb')
    print('--- rgb -> xyz ---')
    print(to_xyz)
    print('--- xyz -> rgb ---')
    print(from_xyz)
