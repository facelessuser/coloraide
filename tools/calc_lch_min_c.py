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
from coloraide.spaces.achromatic import Achromatic  # noqa: E402
from coloraide import algebra as alg  # noqa: E402


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='calc_cam16_ucs_jmh_min_m.py',
        description='Calculate min C for achromatic colors in LCh spaces and map spline against real values.'
    )
    parser.add_argument(
        '-space', '-s', type=str, help="Color space to use."
    )
    # Flag arguments
    parser.add_argument(
        '--res', '-r', type=int, default=50000, help="Resolution to use when calculating range, default is 50000."
    )
    parser.add_argument(
        '--spline', '-S', type=str, default='catrom', help="Spline to use for approximation of achromatic line"
    )
    parser.add_argument(
        '--tuning', '-t', type=str, action='append',
        help="Spline tuning parameters: start:end:step:scale (int:int:int:float)"
    )
    parser.add_argument(
        '--mirror', '-m', action='store_true', help="Mirror response across lightness axis"
    )
    parser.add_argument(
        '--dump', action='store_true', help="Dump calculated values."
    )
    args = parser.parse_args()

    return run(
        args.space,
        args.spline,
        args.tuning,
        args.mirror,
        args.res,
        args.dump
    )


def run(space, spline, tuning, mirror, res, dump):
    """Run."""

    tune = []
    for x in tuning:
        tune.append([int(i) if e < 3 else float(i) for e, i in enumerate(x.split(':'))])

    class Achroma(Achromatic):
        """Setup special dynamic achromatic class."""

        L_IDX = 0
        C_IDX = 1
        H_IDX = 2

        def convert(self, coords, **kwargs):
            """Convert to the target color space."""

            lab = Color('srgb', coords).convert(space)
            l = lab[0]
            c, h = alg.rect_to_polar(*lab[1:-1])
            return l, c, h

    test = Achroma(spline=spline, mirror=mirror)
    test.calc_achromatic_response(tune)

    color = Color('srgb', [0, 0, 0])
    points1 = {}
    points2 = {}
    diff_over = 0
    diff_under = 0
    min_h = float('inf')
    max_h = float('-inf')
    max_c = 0
    first = False

    for i in range(res + 1):
        div = res / 5
        v = i / div
        if v < 0.001:
            continue
        color.update('srgb', [v, v, v])
        lab = color.convert(space, norm=False)
        l = lab[0]
        c, h = alg.rect_to_polar(*lab[1:-1])
        if not first:
            print('Starting L: ', l)
            print('Starting C: ', c)
            first = True

        if c > max_c:
            max_c = c

        if h < min_h:
            min_h = h
        if h > max_h:
            max_h = h

        domain = test.scale(l)
        calc = test.spline(domain)

        delta = calc[1] - c
        if delta >= 0 and delta > diff_over:
            diff_over = delta
        if delta < 0 and abs(delta) > diff_under:
            diff_under = abs(delta)

        points1[l] = (c, h)
        points2[calc[0]] = (calc[1], calc[2])

    print('Delta Over: ', diff_over)
    print('Delta Under: ', diff_under)
    print('Max C: ', max_c)
    print('Hue (low/high) : {} / {}'.format(min_h, max_h))
    print('Data Points: ', test.spline.length)

    l1 = []
    l2 = []
    c1 = []
    c2 = []
    h1 = []
    h2 = []
    for l in sorted(points1):
        l1.append(l)
        c1.append(points1[l][0])
        h1.append(points1[l][1])
    for l in sorted(points2):
        l2.append(l)
        c2.append(points2[l][0])
        h2.append(points2[l][1])

    figure = plt.figure()

    # Create axes
    ax = plt.axes(
        projection='3d',
        xlabel='C',
        ylabel='h',
        zlabel='L'
    )
    # ax.set_aspect('auto')
    ax.set_title('LCh: Delta (over/under) = {:.5g}/{:.5g} - Max C = {:.5g}'.format(diff_over, diff_under, max_c))
    figure.add_axes(ax)

    # Print the calculated line against the real line
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.plot(c1, l1, '.', color='black')
    plt.plot(c2, l2, '.', color='red', markersize=0.5)
    plt.show()

    if dump:
        print('===== Data =====')
        print(test.dump())

    return 0


if __name__ == "__main__":
    sys.exit(main())
