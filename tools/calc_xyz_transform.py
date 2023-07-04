"""Calculate XYZ conversion matrices."""
import sys
import os

sys.path.insert(0, os.getcwd())

from coloraide import util  # noqa: E402
from coloraide import algebra as alg  # noqa: E402

white_d65 = util.xy_to_xyz((0.31270, 0.32900))
white_d50 = util.xy_to_xyz((0.34570, 0.35850))
white_aces = util.xy_to_xyz((0.32168, 0.33767))


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


def get_matrix(wp, space):
    """Get the matrices for the specified space."""

    if space == 'srgb':
        x = [0.64, 0.30, 0.15]
        y = [0.33, 0.60, 0.06]
    elif space == 'display-p3':
        x = [0.68, 0.265, 0.150]
        y = [0.32, 0.69, 0.060]
    elif space == 'rec2020':
        x = [0.708, 0.17, 0.131]
        y = [0.292, 0.797, 0.046]
    elif space == 'a98-rgb':
        x = [0.64, 0.21, 0.15]
        y = [0.33, 0.71, 0.06]
    elif space == 'prophoto-rgb':
        x = [0.7347, 0.1596, 0.0366]
        y = [0.2653, 0.8404, 0.0001]
    elif space == 'aces-ap0':
        x = [0.7347, 0.0, 0.0001]
        y = [0.2653, 1.0, -0.0770]
    elif space == 'aces-ap1':
        x = [0.713, 0.165, 0.128]
        y = [0.293, 0.830, 0.044]
    else:
        raise ValueError

    m = alg.transpose([util.xy_to_xyz(xy) for xy in zip(x, y)])
    mi = alg.inv(m)
    rgb = alg.dot(mi, wp)
    rgb2xyz = alg.multiply(m, rgb)
    xyz2rgb = alg.inv(rgb2xyz)

    return rgb2xyz, xyz2rgb


if __name__ == "__main__":
    print('===== sRGB =====')
    to_xyz, from_xyz = get_matrix(white_d65, 'srgb')
    print('--- rgb -> xyz ---')
    pprint(to_xyz)
    print('--- xyz -> rgb ---')
    pprint(from_xyz)

    print('===== Display P3 =====')
    to_xyz, from_xyz = get_matrix(white_d65, 'display-p3')
    print('--- rgb -> xyz ---')
    pprint(to_xyz)
    print('--- xyz -> rgb ---')
    pprint(from_xyz)

    print('===== Adobe 98 =====')
    to_xyz, from_xyz = get_matrix(white_d65, 'a98-rgb')
    print('--- rgb -> xyz ---')
    pprint(to_xyz)
    print('--- xyz -> rgb ---')
    pprint(from_xyz)

    print('===== Rec.2020 =====')
    to_xyz, from_xyz = get_matrix(white_d65, 'rec2020')
    print('--- rgb -> xyz ---')
    pprint(to_xyz)
    print('--- xyz -> rgb ---')
    pprint(from_xyz)

    print('===== ProPhoto =====')
    to_xyz, from_xyz = get_matrix(white_d50, 'prophoto-rgb')
    print('--- rgb -> xyz ---')
    pprint(to_xyz)
    print('--- xyz -> rgb ---')
    pprint(from_xyz)

    print('===== ACES =====')
    to_xyz, from_xyz = get_matrix(white_aces, 'aces-ap0')
    print('--- rgb -> xyz ---')
    pprint(to_xyz)
    print('--- xyz -> rgb ---')
    pprint(from_xyz)

    print('===== ACEScg =====')
    to_xyz, from_xyz = get_matrix(white_aces, 'aces-ap1')
    print('--- rgb -> xyz ---')
    pprint(to_xyz)
    print('--- xyz -> rgb ---')
    pprint(from_xyz)
