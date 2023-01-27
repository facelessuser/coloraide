"""Plot easing functions."""
import argparse
import sys
import os
import re
import matplotlib.pyplot as plt

sys.path.insert(0, os.getcwd())

from coloraide import easing  # noqa: E402

RE_BEZIER = re.compile(
    r'''(?x)
    ^(cubic_bezier)\((
        (?:\s*[+\-]?(?:[0-9]*\.)?[0-9]+(?:e[-+]?[0-9]*)?\s*,){3}
        \s*[+\-]?(?:[0-9]*\.)?[0-9]+(?:e[-+]?[0-9]*)?\s*
    )\)$
    '''
)


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='easing_diagrams', description='Plot easings.')
    parser.add_argument('--easing', '-s', default='linear', help="Space to interpolate in.")
    parser.add_argument('--extrapolate', '-e', action='store_true', help='Extrapolate values.')
    parser.add_argument('--title', '-T', default='', help="Provide a title for the diagram.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    args = parser.parse_args()

    m = RE_BEZIER.match(args.easing.strip())
    if m is not None:
        function = m.group(0).strip()
        ease = getattr(easing, 'cubic_bezier')(*[float(v.strip()) for v in m.group(2).split(',')])
    else:
        function = args.easing.strip()
        ease = getattr(easing, function)

    xs = []
    ys = []
    if not args.extrapolate:
        offset, factor = 0, 100
    else:
        offset, factor = 25, 50
    for r in range(101):
        x = (r - offset) / factor
        xs.append(x)
        ys.append(ease(x))

    plt.style.use('seaborn-v0_8-darkgrid')
    default_color = 'black'

    figure = plt.figure()

    # Create axes
    ax = plt.axes(
        xlabel='Time',
        ylabel='Progression'
    )

    ax.set_aspect('equal')

    # Create titles
    title = args.title
    if not title:
        title = function
    ax.set_title(title)

    figure.add_axes(ax)

    p0 = [0, 0]
    p3 = [1, 1]
    if function == 'linear':
        p1 = [0.0, 0.0]
        p2 = [1.0, 1.0]
    else:
        p1 = ease.keywords['p1']
        p2 = ease.keywords['p2']

    plt.plot(
        xs,
        ys,
        color=default_color,
        marker="",
        linewidth=1.5,
        markersize=2,
        antialiased=True
    )

    plt.plot(
        [p0[0], p1[0]],
        [p0[1], p1[1]],
        '--',
        color='teal',
        marker="",
        linewidth=1.5,
        markersize=2,
        antialiased=True
    )

    plt.plot(
        [p2[0], p3[0]],
        [p2[1], p3[1]],
        '--',
        color='teal',
        marker="",
        linewidth=1.5,
        markersize=2,
        antialiased=True
    )

    plt.scatter(
        [p0[0], p3[0]],
        [p0[1], p3[1]],
        marker='o',
        color='black',
        zorder=2
    )

    plt.scatter(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        marker='o',
        color='teal',
        zorder=2
    )

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
