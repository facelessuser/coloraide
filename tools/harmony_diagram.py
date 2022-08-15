"""Harmony diagram."""
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


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='gamut_diagrams', description='Demonstrate gamut mapping.')
    parser.add_argument('--space', '-s', default='hsl', help="Space to interpolate in.")
    parser.add_argument('--color', '-c', help="Seed color.")
    parser.add_argument('--harmony', '-n', default='complement', help="Color harmony to use.")
    parser.add_argument('--gamut', '-g', default="srgb", help='Gamut to evaluate the color in (default is sRGB).')
    parser.add_argument('--map-colors', '-m', action='store_true', help="Gamut map colors to be within the gamut.")
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument('--yaxis', '-y', help="The channel to plot on Y axis (other than hue or l) 'name:min:max'.")
    parser.add_argument('--resolution', '-r', default="800", help="How densely to render the figure.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')

    args = parser.parse_args()

    c1 = Color(args.color).convert(args.space)

    names = set(c1._space.CHANNELS + tuple(c1._space.CHANNEL_ALIASES.keys()))

    for c_name in ('lightness', 'intensity', 'l', 'i'):
        if c_name in names:
            c_value = c1[c_name]
            break
    else:
        raise ValueError('Cannot find a lightness equivalence')

    if 'hue' not in names:
        raise ValueError('Expected a color space with a "hue" attribute.')

    if not args.title:
        title = "Color Harmony '{}'' in Color Space '{}' in Gamut '{}'".format(args.harmony, args.space, args.gamut)
    else:
        title = args.title

    subtitle = 'Initial Color: {}'.format(c1.to_string())

    plot_slice(
        args.space,
        '{}:{}'.format(c_name, c_value),
        'hue:0:360',
        args.yaxis,
        gamut=args.gamut,
        resolution=int(args.resolution),
        title=title,
        subtitle=subtitle,
        dark=args.dark,
        polar=True
    )

    # Get the actual indexes of the specified channels
    name2 = args.yaxis.split(":", 1)[0]
    name2 = c1._space.CHANNEL_ALIASES.get(name2, name2)

    colors = c1.harmony(args.harmony, space=args.space)
    if args.map_colors:
        [c.fit(args.gamut) for c in colors]

    for c in colors:
        plt.scatter(
            math.radians(c.get('hue')),
            c.get(name2),
            marker="o",
            color=c.convert('srgb').to_string(hex=True),
            edgecolor='black',
            s=8 ** 2,
            zorder=100
        )
        xs = [0, math.radians(c.get('hue'))]
        ys = [0, c.get(name2)]

        plt.plot(
            xs,
            ys,
            color='black',
            marker="",
            linewidth=1.5,
            markersize=2,
            antialiased=True
        )

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
