"""
Model interpolation.

Currently only shows non polar interpolation.
"""
import sys
import os
import matplotlib.pyplot as plt
import argparse
import math
import numpy as np
from scipy import interpolate

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras import Color
except ImportError:
    from coloraide import Color
from tools.slice_diagram import plot_slice  # noqa: E402
from coloraide.util import fmt_float  # noqa: E402
from coloraide.spaces import Cylindrical  # noqa: E402


def get_spline(x, y, points=100):
    """Get spline."""

    # Setup as `numpy` arrays
    x2 = np.asarray(x, dtype=float)
    y2 = np.asarray(y, dtype=float)

    # Create a linear spaces between 0 and 1 for our curve
    path = np.linspace(0, 1, x2.size)

    # Create the position vectors using x and y coordinates
    vec = np.vstack((x2.reshape((1, x2.size)), y2.reshape((1, y2.size))))

    # Create the spline function
    spline = interpolate.interp1d(path, vec, kind='cubic')

    # Get the actual spline curve between 0 and 1 with number of points
    x2, y2 = spline(np.linspace(np.min(path), np.max(path), points))
    return x2.tolist(), y2.tolist()


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='gamut_diagrams', description='Demonstrate gamut mapping.')
    parser.add_argument('--space', '-s', default='srgb', help="Space to interpolate in.")
    parser.add_argument('--color1', '-a', help="Starting color.")
    parser.add_argument('--color2', '-b', help="Ending color.")
    parser.add_argument('--position', '-p', default=0.5, type=float, help="Position between to show interpolated.")
    parser.add_argument('--gamut', '-g', default="srgb", help='Gamut to evaluate the color in (default is sRGB).')
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument(
        '--constant',
        '-c',
        help=(
            "The channel to hold constant and the value to use 'name:value'. This will overwrite whatever the start"
            " and end color specifies as the plot must fit in the 2D plane."
        )
    )
    parser.add_argument('--xaxis', '-x', help="The channel to plot on X axis 'name:range:offset'.")
    parser.add_argument('--yaxis', '-y', help="The channel to plot on Y axis 'name:range:offset'.")
    parser.add_argument('--resolution', '-r', default="800", help="How densely to render the figure.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')

    args = parser.parse_args()

    c_name, c_value = args.constant.split(':')
    c_value = float(c_value)
    c1 = Color(args.color1).convert(args.space)
    c2 = Color(args.color2).convert(args.space)
    if c1.get(c_name) != c_value:
        c1.set(c_name, c_value)
    if c2.get(c_name) != c_value:
        c2.set(c_name, c_value)

    if not args.title:
        title = "Interpolation in the {} Color Space Using the {} Gamut".format(args.space, args.gamut)
    else:
        title = args.title

    subtitle = '{} and {} @ {}%'.format(c1.to_string(), c2.to_string(), fmt_float(args.position * 100, 5))

    plot_slice(
        args.space,
        args.constant,
        args.xaxis,
        args.yaxis,
        gamut=args.gamut,
        resolution=int(args.resolution),
        title=title,
        subtitle=subtitle,
        dark=args.dark,
        polar=True
    )

    # Get the actual indexes of the specified channels
    name1 = args.xaxis.split(":", 1)[0]
    name2 = args.yaxis.split(":", 1)[0]
    name1 = c1._space.CHANNEL_ALIASES.get(name1, name1)
    index1 = c1._space.CHANNEL_NAMES.index(name1)
    name2 = c1._space.CHANNEL_ALIASES.get(name2, name2)
    hue_index = -1

    if isinstance(c1._space, Cylindrical):
        index = c1._space.hue_index()
        if index == index1:
            hue_index = index

    c3 = c1.interpolate(c2, space=args.space)(float(args.position))

    xs = []
    ys = []
    for item in c1.steps(c2, steps=100, space=args.space):
        xs.append(item.get(name1) if hue_index == -1 else math.radians(item.get(name1)))
        ys.append(item.get(name2))

    xs, ys = get_spline(xs, ys, len(xs) * 3)

    plt.plot(
        xs,
        ys,
        color='black',
        marker="",
        linewidth=1.5,
        markersize=2,
        antialiased=True
    )

    plt.scatter(
        c1.get(name1) if hue_index == -1 else math.radians(c1.get(name1)),
        c1.get(name2),
        marker="o",
        color=c1.convert('srgb').to_string(hex=True),
        edgecolor='black',
        zorder=100
    )

    plt.scatter(
        c2.get(name1) if hue_index == -1 else math.radians(c2.get(name1)),
        c2.get(name2),
        marker="o",
        color=c2.convert('srgb').to_string(hex=True),
        edgecolor='black',
        zorder=100
    )

    plt.scatter(
        c3.get(name1) if hue_index == -1 else math.radians(c3.get(name1)),
        c3.get(name2),
        marker="o",
        color=c3.convert('srgb').to_string(hex=True),
        edgecolor='black',
        zorder=100
    )

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
