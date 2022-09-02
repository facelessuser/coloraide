"""Calculate XYZ conversion matrices."""
import sys
import os
from fractions import Fraction

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

import tools.falgebra as alg  # noqa: E402
from coloraide import util  # noqa: E402

white_d65 = util.xy_to_xyz((Fraction(3127, 10000), Fraction(3290, 10000)), alg.ONE, alg.ONE)
white_d50 = util.xy_to_xyz((Fraction(3457, 10000), Fraction(3585, 10000)), alg.ONE, alg.ONE)
white_aces = util.xy_to_xyz((Fraction(32168, 100000), Fraction(33767, 100000)), alg.ONE, alg.ONE)


def pprint(value):
    """Print the matrix."""
    print('[', end='')
    first = True
    for v in value:
        if first:
            first = False
        else:
            print(',\n ', end='')
        if isinstance(v, Fraction):
            print(v.numerator / v.denominator, end='')
        else:
            print([c.numerator / c.denominator if isinstance(c, Fraction) else c for c in v], end='')
    print(']')


def get_matrix(wp, space):
    """Get the matrices for the specified space."""

    if space == 'srgb':
        x = [Fraction(64, 100), Fraction(30, 100), Fraction(15, 100)]
        y = [Fraction(33, 100), Fraction(60, 100), Fraction(6, 100)]
    elif space == 'display-p3':
        x = [Fraction(68, 100), Fraction(265, 1000), Fraction(15, 100)]
        y = [Fraction(32, 100), Fraction(69, 100), Fraction(6, 100)]
    elif space == 'rec2020':
        x = [Fraction(708, 1000), Fraction(17, 100), Fraction(131, 1000)]
        y = [Fraction(292, 1000), Fraction(797, 1000), Fraction(46, 1000)]
    elif space == 'a98-rgb':
        x = [Fraction(64, 100), Fraction(21, 100), Fraction(15, 100)]
        y = [Fraction(33, 100), Fraction(71, 100), Fraction(6, 100)]
    elif space == 'prophoto-rgb':
        x = [Fraction(734699, 1000000), Fraction(159597, 1000000), Fraction(36598, 1000000)]
        y = [Fraction(265301, 1000000), Fraction(840403, 1000000), Fraction(105, 1000000)]
    elif space == 'aces-ap0':
        x = [Fraction(7347, 10000), Fraction(0, 1), Fraction(1, 10000)]
        y = [Fraction(2653, 10000), Fraction(1, 1), Fraction(-770, 10000)]
    elif space == 'aces-ap1':
        x = [Fraction(713, 1000), Fraction(165, 1000), Fraction(128, 1000)]
        y = [Fraction(293, 1000), Fraction(830, 1000), Fraction(44, 1000)]
    else:
        raise ValueError

    m = alg.transpose([util.xy_to_xyz(xy, alg.ONE, alg.ONE) for xy in zip(x, y)])
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

    print('===== ACEScc =====')
    to_xyz, from_xyz = get_matrix(white_aces, 'aces-ap1')
    print('--- rgb -> xyz ---')
    pprint(to_xyz)
    print('--- xyz -> rgb ---')
    pprint(from_xyz)
