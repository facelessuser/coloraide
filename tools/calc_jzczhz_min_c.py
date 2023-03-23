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
from coloraide.spaces.jzczhz import Achromatic  # noqa: E402


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
        '--spline', '-S', type=str, default='catrom', help="Spline to use for approximation of achromatic line"
    )
    parser.add_argument(
        '--low', '-L', type=str, default='1:5:1:1000.0',
        help="Tuning for low range: start:end:step:scale (int:int:int:float)"
    )
    parser.add_argument(
        '--mid', '-M', type=str, default='1:9:2:200.0',
        help="Tuning for mid range: start:end:step:scale (int:int:int:float)"
    )
    parser.add_argument(
        '--high', '-H', type=str, default='5:521:5:100.0',
        help="Tuning for high range: start:end:step:scale (int:int:int:float)"
    )
    parser.add_argument(
        '--dump', action='store_true', help="Dump calculated values."
    )
    args = parser.parse_args()

    return run(
        args.spline,
        args.low,
        args.mid,
        args.high,
        args.res,
        args.dump
    )


def run(spline, low, mid, high, res, dump):
    """Run."""

    tuning = {
        "low": [int(i) if e < 3 else float(i) for e, i in enumerate(low.split(':'))],
        "mid": [int(i) if e < 3 else float(i) for e, i in enumerate(mid.split(':'))],
        "high": [int(i) if e < 3 else float(i) for e, i in enumerate(high.split(':'))]
    }

    test = Achromatic(tuning, 1, 1, 100, spline)

    color = Color('srgb', [0, 0, 0])
    points1 = {}
    points2 = {}
    diff_over = 0
    diff_under = 0
    max_c = 0
    first = False

    for i in range(res + 1):
        div = res / 5
        v = i / div
        if v < 0.001:
            continue
        color.update('srgb', [v, v, v])
        j, c, h = color.convert('jzczhz', norm=False)[:-1]
        if not first:
            print('Starting J: ', j)
            print('Starting C: ', c)
            first = True

        if c > max_c:
            max_c = c

        domain = test.scale(j)
        calc = test.spline(domain)

        delta = calc[1] - c
        if delta >= 0 and delta > diff_over:
            diff_over = delta
        if delta < 0 and abs(delta) > diff_under:
            diff_under = abs(delta)

        points1[j] = (c, h)
        points2[calc[0]] = (calc[1], calc[2])

    print('Delta Over: ', diff_over)
    print('Delta Under: ', diff_under)
    print('Max M: ', max_c)
    print('Data Points: ', test.spline.length)

    j1 = []
    j2 = []
    c1 = []
    c2 = []
    h1 = []
    h2 = []
    for j in sorted(points1):
        j1.append(j)
        c1.append(points1[j][0])
        h1.append(points1[j][1])
    for j in sorted(points2):
        j2.append(j)
        c2.append(points2[j][0])
        h2.append(points2[j][1])

    figure = plt.figure()

    # Create axes
    ax = plt.axes(
        projection='3d',
        xlabel='C',
        ylabel='H',
        zlabel='J'
    )
    # ax.set_aspect('auto')
    ax.set_title('JMh: Delta = {} - Max C = {}'.format(max(diff_over, diff_under), max_c))
    figure.add_axes(ax)

    # Print the calculated line against the real line
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.plot(c1, j1, '.', color='black')
    plt.plot(c2, j2, '.', color='red', markersize=0.5)
    plt.show()

    if dump:
        print('===== Data =====')
        print(test.dump())

    return 0


if __name__ == "__main__":
    sys.exit(main())
