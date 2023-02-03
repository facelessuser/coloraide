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
        '--spline', '-S', type=str, default='natural', help="Spline to use for approximation of achromatic line"
    )
    parser.add_argument(
        '--low', '-L', type=str, default='0:51:1:200.0',
        help="Tuning for low range: start:end:step:scale (int:int:int:float)"
    )
    parser.add_argument(
        '--mid', '-M', type=str, default='50:101:5:100.0',
        help="Tuning for mid range: start:end:step:scale (int:int:int:float)"
    )
    parser.add_argument(
        '--high', '-H', type=str, default='101:502:25:75.0',
        help="Tuning for high range: start:end:step:scale (int:int:int:float)"
    )
    args = parser.parse_args()

    return run(args.spline, args.low, args.mid, args.high, args.res)


def run(spline, low, mid, high, res):
    """Run."""

    tuning = {
        "low": [int(i) if e < 3 else float(i) for e, i in enumerate(low.split(':'))],
        "mid": [int(i) if e < 3 else float(i) for e, i in enumerate(mid.split(':'))],
        "high": [int(i) if e < 3 else float(i) for e, i in enumerate(high.split(':'))]
    }
    env = HCT.ENV
    test = Achromatic(tuning, 0.06, env, spline)

    color = Color('srgb', [0, 0, 0])
    points1 = {}
    points2 = {}
    diff = 0
    max_m = 0

    for i in range(res + 1):
        div = res / 5
        color.update('srgb', [i / div, i / div, i / div])
        xyz = color.convert('xyz-d65')
        m, t = xyz_to_hct(xyz[:-1], HCT.ENV)[1:]

        if m > max_m:
            max_m = m

        domain = test.scale(t)
        calc = test.spline(domain)

        delta = abs(calc[1] - m)
        if delta > diff:
            diff = delta

        points1[t] = m
        points2[calc[0]] = calc[1]

    print('Delta: ', diff)
    print('Max Chroma: ', max_m)

    t1 = []
    t2 = []
    m1 = []
    m2 = []
    for t in sorted(points1):
        t1.append(t)
        m1.append(points1[t])
    for t in sorted(points2):
        t2.append(t)
        m2.append(points2[t])

    figure = plt.figure()

    # Create axes
    ax = plt.axes(
        xlabel='C',
        ylabel='T'
    )
    ax.set_aspect('auto')
    ax.set_title('HCT: Delta = {} - Max C = {}'.format(diff, max_m))
    figure.add_axes(ax)

    # Print the calculated line against the real line
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.plot(m1, t1, '.', color='black')
    plt.plot(m2, t2, '.', color='red', markersize=0.5)
    plt.show()

    return 0


if __name__ == "__main__":
    sys.exit(main())
