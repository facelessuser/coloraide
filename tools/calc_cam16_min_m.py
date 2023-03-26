"""
Map our achromatic spline calculation against real achromatic response.

Report the delta between our spline and the real world. Also note the highest chroma climbs.
"""
import sys
import argparse
import os
import matplotlib.pyplot as plt
import math

sys.path.insert(0, os.getcwd())

from coloraide.everything import ColorAll as Color  # noqa: E402
from coloraide.spaces.cam16_jmh import Environment, xyz_d65_to_cam16, Achromatic  # noqa: E402
from coloraide.cat import WHITES  # noqa: E402


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='calc_cam16_ucs_jmh_min_m.py',
        description='Calculate min M for achromatic colors in CAM16 UCS JMh and map current spline against real values.'
    )
    # Flag arguments
    parser.add_argument(
        '--res', '-r', type=int, default=50000, help="Resolution to use when calculating range, default is 50000."
    )
    parser.add_argument(
        '--white-point', '-w', type=str, default='2deg:D65', help="White point 'deg:wp', example: '2deg:D65'."
    )
    parser.add_argument(
        '--adapting-luminance', '-a', type=float, default=64 / math.pi * 0.2, help="Adapting luminance."
    )
    parser.add_argument(
        '--background-luminance', '-b', type=float, default=20, help="Background luminace - default 20 (gray world)."
    )
    parser.add_argument(
        '--surround', '-s', type=str, default='average', help="Surround: 'average', 'dim', 'dark'"
    )
    parser.add_argument(
        '--discounting', '-d', action='store_true', help="Enable discounting."
    )
    parser.add_argument(
        '--spline', '-S', type=str, default='catrom', help="Spline to use for approximation of achromatic line"
    )
    parser.add_argument(
        '--tuning', '-t', type=str, action='append',
        help="Spline tuning parameters: start:end:step:scale (int:int:int:float)"
    )
    parser.add_argument(
        '--dump', action='store_true', help="Dump calculated values."
    )
    args = parser.parse_args()

    return run(
        args.white_point,
        args.adapting_luminance,
        args.background_luminance,
        args.surround,
        args.discounting,
        args.spline,
        args.tuning,
        args.res,
        args.dump
    )


def run(white_point, la, ba, surround, discounting, spline, tuning, res, dump):
    """Run."""

    deg, wp = white_point.split(':')
    tune = []
    for x in tuning:
        tune.append([int(i) if e < 3 else float(i) for e, i in enumerate(x.split(':'))])

    env = Environment(WHITES[deg][wp], la, ba, surround, discounting)
    convert = xyz_d65_to_cam16

    test = Achromatic(spline=spline, env=env)
    test.calc_achromatic_response(tune, env=env)

    color = Color('srgb', [0, 0, 0])
    points1 = {}
    points2 = {}
    diff_over = 0
    diff_under = 0
    max_m = 0
    first = False

    for i in range(1, res + 1):
        div = res / 5
        v = i / div
        if v < 0.001:
            continue
        color.update('srgb', [v, v, v])
        xyz = color.convert('xyz-d65')
        coords = convert(xyz[:-1], env)[:]
        j, m, h = coords[0], coords[5], coords[2]
        if not first:
            print('Starting J: ', j)
            print('Starting M: ', m)
            first = True

        if m > max_m:
            max_m = m

        if not env.discounting:
            domain = test.scale(j)
            calc = test.spline(domain)
        else:
            calc = (j, 1e-08, 0.0)

        delta = calc[1] - m
        if delta >= 0 and delta > diff_over:
            diff_over = delta
        if delta < 0 and abs(delta) > diff_under:
            diff_under = abs(delta)

        points1[j] = (m, h)
        points2[calc[0]] = (calc[1], calc[2])

    print('Delta Over: ', diff_over)
    print('Delta Under: ', diff_under)
    print('Max M: ', max_m)
    if not env.discounting:
        print('Data Points: ', test.spline.length)

    j1 = []
    j2 = []
    m1 = []
    m2 = []
    h1 = []
    h2 = []
    for j in sorted(points1):
        j1.append(j)
        m1.append(points1[j][0])
        h1.append(points1[j][1])
    for j in sorted(points2):
        j2.append(j)
        m2.append(points2[j][0])
        h2.append(points2[j][1])

    figure = plt.figure()

    ax = plt.axes(
        projection='3d',
        xlabel='M',
        ylabel='H',
        zlabel='J'
    )

    # ax.set_aspect('auto')
    ax.set_title('JMh: Delta = {} - Max M = {}'.format(max(diff_over, diff_under), max_m))
    figure.add_axes(ax)

    # Print the calculated line against the real line
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.plot(m1, h1, j1, '.', color='black')
    plt.plot(m2, h2, j2, '.', color='red', markersize=0.5)
    plt.show()

    if dump:
        print('===== Data =====')
        print(test.dump())

    return 0


if __name__ == "__main__":
    sys.exit(main())
