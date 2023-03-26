"""
Map our achromatic spline calculation against real achromatic response.

Report the delta between our spline and the real world. Also note the highest chroma climbs.
"""
import sys
import argparse
import os
import matplotlib.pyplot as plt

sys.path.insert(0, os.getcwd())

from coloraide.everything import ColorAll as Color  # noqa: E402
from coloraide.spaces.hct import HCT, xyz_to_hct, Achromatic  # noqa: E402


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='calc_hct_min_chroma.py',
        description='Calculate minimum chroma for achromatic colors in HCT and maps current spline against real values.'
    )
    # Flag arguments
    parser.add_argument(
        '--res', '-r', type=int, default=50000, help="Resolution to use when calculating range, default is 10000."
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

    return run(args.spline, args.tuning, args.res, args.dump)


def run(spline, tuning, res, dump):
    """Run."""

    tune = []
    for x in tuning:
        tune.append([int(i) if e < 3 else float(i) for e, i in enumerate(x.split(':'))])
    env = HCT.ENV
    test = Achromatic(spline=spline, env=env)
    test.calc_achromatic_response(tune, env=env)

    color = Color('srgb', [0, 0, 0])
    points1 = {}
    points2 = {}
    diff_over = 0
    diff_under = 0
    max_m = 0
    first = False

    for i in range(res + 1):
        div = res / 5
        v = i / div
        if v < 0.001:
            continue
        color.update('srgb', [v, v, v])
        xyz = color.convert('xyz-d65')
        h, c, t = xyz_to_hct(xyz[:-1], HCT.ENV)
        if not first:
            print('Starting T: ', t)
            print('Starting C: ', c)
            first = True

        if c > max_m:
            max_m = c

        domain = test.scale(t)
        calc = test.spline(domain)

        delta = calc[1] - c
        if delta >= 0 and delta > diff_over:
            diff_over = delta
        if delta < 0 and abs(delta) > diff_under:
            diff_under = abs(delta)

        points1[t] = (c, h)
        points2[calc[0]] = (calc[1], calc[2])

    print('Delta Over: ', diff_over)
    print('Delta Under: ', diff_under)
    print('Max M: ', max_m)
    print('Data Points: ', test.spline.length)

    t1 = []
    t2 = []
    m1 = []
    m2 = []
    h1 = []
    h2 = []
    for t in sorted(points1):
        t1.append(t)
        m1.append(points1[t][0])
        h1.append(points1[t][1])
    for t in sorted(points2):
        t2.append(t)
        m2.append(points2[t][0])
        h2.append(points2[t][1])

    figure = plt.figure()

    # Create axes
    ax = plt.axes(
        projection='3d',
        xlabel='C',
        ylabel='H',
        zlabel='T'
    )

    ax.set_aspect('auto')
    ax.set_title('HCT: Delta = {} - Max C = {}'.format(max(diff_over, diff_under), max_m))
    figure.add_axes(ax)

    # Print the calculated line against the real line
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.plot(m1, h1, t1, '.', color='black')
    plt.plot(m2, h2, t2, '.', color='red', markersize=0.5)
    plt.show()

    if dump:
        print('===== Data =====')
        print(test.dump())

    return 0


if __name__ == "__main__":
    sys.exit(main())
