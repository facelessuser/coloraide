"""Calculate XYZ conversion matrices."""
import numpy as np

np.set_printoptions(precision=None, sign='-', floatmode='unique')


def xy_to_xyz(x, y):
    """Convert `xyY` to `xyz`."""

    return [x / y, 1, (1 - x - y) / y]


white_d65 = np.asfarray(xy_to_xyz(0.31270, 0.32900))
white_d50 = np.asfarray(xy_to_xyz(0.34570, 0.35850))


def get_matrix(wp, space):
    """Get the matrices for the specified space."""

    if space == 'srgb':
        x = np.asfarray([0.64, 0.30, 0.15])
        y = np.asfarray([0.33, 0.60, 0.06])
    elif space == 'display-p3':
        x = np.asfarray([0.68, 0.265, 0.150])
        y = np.asfarray([0.32, 0.69, 0.060])
    elif space == 'rec2020':
        x = np.asfarray([0.708, 0.17, 0.131])
        y = np.asfarray([0.292, 0.797, 0.046])
    elif space == 'a98-rgb':
        x = np.asfarray([0.64, 0.21, 0.15])
        y = np.asfarray([0.33, 0.71, 0.06])
    elif space == 'prophoto-rgb':
        x = np.asfarray([0.7347, 0.1596, 0.0366])
        y = np.asfarray([0.2653, 0.8404, 0.0001])
    else:
        raise ValueError

    one = np.float64(1.0)
    m = np.asfarray(
        [
            [x[0] / y[0], one, (one - x[0] - y[0]) / y[0]],
            [x[1] / y[1], one, (one - x[1] - y[1]) / y[1]],
            [x[2] / y[2], one, (one - x[2] - y[2]) / y[2]]
        ]
    )
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
