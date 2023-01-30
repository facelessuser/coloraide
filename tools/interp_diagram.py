"""
Model interpolation.

Currently only shows non polar interpolation.
"""
import sys
import os
import matplotlib.pyplot as plt
import argparse
import math

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from tools.slice_diagram import plot_slice  # noqa: E402
from coloraide.spaces import Cylindrical  # noqa: E402
from coloraide import algebra as alg  # noqa: E402


def get_spline(x, y, steps=100):
    """Get spline."""

    return tuple([list(i) for i in zip(*alg.interpolate(list(zip(x, y)), method='monotone').steps(steps))])


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='gamut_diagrams', description='Demonstrate gamut mapping.')
    parser.add_argument('--space', '-s', default='srgb', help="Space to interpolate in.")
    parser.add_argument('--color', '-c', action='append', help="Color.")
    parser.add_argument('--position', '-p', type=float, help="Position between to show interpolated.")
    parser.add_argument('--gamut', '-g', default="srgb", help='Gamut to evaluate the color in (default is sRGB).')
    parser.add_argument('--method', '-m', default='linear', help="Interplation method to use: linear, bezier, etc.")
    parser.add_argument('--extrapolate', '-e', action='store_true', help='Extrapolate values.')
    parser.add_argument('--title', '-T', default='', help="Provide a title for the diagram.")
    parser.add_argument('--subtitle', '-t', default='', help="Provide a subtitle for the diagram.")
    parser.add_argument(
        '--constant',
        '-k',
        help=(
            "The channel to hold constant and the value to use 'name:value'. This will overwrite whatever the start"
            " and end color specifies as the plot must fit in the 2D plane."
        )
    )
    parser.add_argument('--xaxis', '-x', help="The channel to plot on X axis 'name:min:max'.")
    parser.add_argument('--yaxis', '-y', help="The channel to plot on Y axis 'name:min:max'.")
    parser.add_argument('--resolution', '-r', default="800", help="How densely to render the figure.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')

    args = parser.parse_args()

    colors = []
    for color in args.color:
        c = Color(color).convert(args.space)
        colors.append(c)

    for chan in args.constant.split(';'):
        c_name, c_value = chan.split(':')
        c_value = float(c_value)
        for color in colors:
            color.set(c_name, c_value)

    if not args.title:
        title = "Interpolation in the {} Color Space Using the {} Gamut".format(args.space, args.gamut)
    else:
        title = args.title

    plot_slice(
        args.space,
        args.constant,
        args.xaxis,
        args.yaxis,
        gamut=args.gamut,
        resolution=int(args.resolution),
        title=title,
        subtitle=args.subtitle,
        dark=args.dark,
        polar=True
    )

    # Get the actual indexes of the specified channels
    c1 = colors[0]
    name1 = args.xaxis.split(":", 1)[0]
    name2 = args.yaxis.split(":", 1)[0]
    name1 = c1._space.CHANNEL_ALIASES.get(name1, name1)
    index1 = c1._space.get_channel_index(name1)
    name2 = c1._space.CHANNEL_ALIASES.get(name2, name2)
    hue_index = -1

    if isinstance(c1._space, Cylindrical):
        index = c1._space.hue_index()
        if index == index1:
            hue_index = index

    xs = []
    ys = []
    i = Color.interpolate(colors, space=args.space, method=args.method, extrapolate=args.extrapolate)
    if not args.extrapolate:
        offset, factor = 0, 1
    else:
        offset, factor = 1, 3
    for r in range(101):
        c = i((r * factor / 100) - offset)
        xs.append(c.get(name1) if hue_index == -1 else math.radians(c.get(name1)))
        ys.append(c.get(name2))

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

    for c in colors:
        plt.scatter(
            c.get(name1) if hue_index == -1 else math.radians(c.get(name1)),
            c.get(name2),
            marker="o",
            color=c.convert('srgb').to_string(hex=True),
            edgecolor='black',
            zorder=100
        )

    if args.position is not None:
        cp = Color.interpolate(colors, space=args.space, method=args.method)(float(args.position))
        plt.scatter(
            cp.get(name1) if hue_index == -1 else math.radians(cp.get(name1)),
            cp.get(name2),
            marker="o",
            color=cp.convert('srgb').to_string(hex=True),
            edgecolor='black',
            s=64,
            zorder=100
        )

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
