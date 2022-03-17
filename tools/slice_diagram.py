"""
Slice diagrams.

Show a slice of a color space where we plot the relation between two channels holding one constant.

Channels to be plotted are given in the form `name:distance:offset`. For instance `a:1:-0.5` would plot the `a` channel
from -0.5 to 0.5.

The constant channel is given in the form `name:value` where value is the constant value for the channel.
"""
import itertools
import matplotlib.pyplot as plt
import argparse
import sys
import os
import math

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras import Color
except ImportError:
    from coloraide import Color
from coloraide import NaN  # noqa: E402
from coloraide.util import fmt_float  # noqa: E402
from coloraide.spaces import Cylindrical  # noqa: E402


def needs_lchuv_workaround(color):
    """
    Check if LCHuv has high chroma and no lightness.

    LCHuv will have such values all in gamut and create weird graphs.
    This is just due to how LCHuv algorithm handles high chroma and zero lightness,
    it all gets treated as black which is in gamut for almost any color.
    """

    return color.space().startswith('lchuv') and color.l == 0 and not color.normalize().is_nan('hue')


def plot_slice(
    space,
    channel0,
    channel1,
    channel2,
    gamut='srgb',
    resolution=500,
    dark=False,
    title="",
    subtitle='',
    polar=False
):
    """Plot a slice."""

    res = resolution
    if not dark:
        plt.style.use('seaborn-darkgrid')
        default_color = 'black'
    else:
        plt.style.use('dark_background')
        default_color = 'white'

    figure = plt.figure()

    # Create a color object based on the specified space.
    c = Color(space, [])

    # Parse the channel strings into actual values
    name0, value = [
        c if i == 0 else float(c if c != 'none' else 'nan') for i, c in enumerate(channel0.split(":"), 0)
    ]
    name1, factor1, offset1 = [
        c if i == 0 else float(c if c != 'none' else 'nan') for i, c in enumerate(channel1.split(':'), 0)
    ]
    name2, factor2, offset2 = [
        c if i == 0 else float(c if c != 'none' else 'nan') for i, c in enumerate(channel2.split(':'), 0)
    ]

    # Get the actual indexes of the specified channels
    name0 = c._space.CHANNEL_ALIASES.get(name0, name0)
    index0 = c._space.CHANNEL_NAMES.index(name0)
    name1 = c._space.CHANNEL_ALIASES.get(name1, name1)
    index1 = c._space.CHANNEL_NAMES.index(name1)
    name2 = c._space.CHANNEL_ALIASES.get(name2, name2)
    index2 = c._space.CHANNEL_NAMES.index(name2)
    hue_index = -1

    kwargs = {}
    if polar and isinstance(c._space, Cylindrical):
        kwargs['projection'] = 'polar'
        index = c._space.hue_index()
        if index == index1:
            hue_index = index

    # Arrays for data points to plot
    c_map = []
    xaxis = []
    yaxis = []

    # Track minimum and maximum values
    c1_mn = float('inf')
    c1_mx = float('-inf')
    c2_mn = float('inf')
    c2_mx = float('-inf')

    # Track the edge of the graphed shape.
    edge_map = {}

    # Iterate through the two specified channels
    for c1, c2 in itertools.product(
        ((x / res * factor1) + offset1 for x in range(0, res + 1)),
        ((x / res * factor2) + offset2 for x in range(0, res + 1))
    ):
        # Set the appropriate channels and update the color object
        coords = [NaN] * 3
        coords[index0] = value
        coords[index1] = c1
        coords[index2] = c2
        c.update(space, coords)

        # Only process colors within the gamut of sRGB.
        if c.in_gamut(gamut, tolerance=0) and not needs_lchuv_workaround(c):
            if hue_index != -1:
                c1 = math.radians(c1)

            # Get the absolute min and max value plotted
            if c1 < c1_mn:
                c1_mn = c1
            if c1 > c1_mx:
                c1_mx = c1

            if c2 < c2_mn:
                c2_mn = c2
            if c2 > c2_mx:
                c2_mx = c2

            # Create an edge map so we can draw an outline
            if c1 not in edge_map:
                mn = mx = c2
            else:
                mn, mx = edge_map[c1]
                if c2 < mn:
                    mn = c2
                elif c2 > mx:
                    mx = c2
            edge_map[c1] = [mn, mx]

            # Save the points
            xaxis.append(c1)
            yaxis.append(c2)
            c_map.append(c.convert('srgb').to_string(hex=True))

    # Create a border around the data
    xe = []
    ye = []
    xtemp = []
    ytemp = []
    for p1, edges in edge_map.items():
        if hue_index == -1:
            xe.append(p1)
            ye.append(edges[0])
            xtemp.append(p1)
            ytemp.append(edges[1])
        else:
            xe.append(p1)
            ye.append(edges[1])

    if hue_index == -1:
        xe.extend(reversed(xtemp))
        ye.extend(reversed(ytemp))
        xe.append(xe[0])
        ye.append(ye[0])

    ax = plt.axes(
        xlabel='{}: {} - {}'.format(name1, fmt_float(c1_mn, 5), fmt_float(c1_mx, 5)),
        ylabel='{}: {} - {}'.format(name2, fmt_float(c2_mn, 5), fmt_float(c2_mx, 5)),
        **kwargs
    )

    if not title:
        title = "Plot of {} showing '{}' and '{}' with '{}' at {}".format(
            space, name1, name2, name0, fmt_float(value, 5)
        )

    plt.suptitle(title)
    if subtitle:
        if hue_index == -1:
            ax.set_title(subtitle, fontdict={'fontsize': 8})
        else:
            ax.set_title(subtitle, fontdict={'fontsize': 8}, pad=2)

    ax.set_aspect('auto' if hue_index == -1 else 'equal')
    figure.add_axes(ax)

    plt.plot(xe, ye, color=default_color, marker="", linewidth=2, markersize=0, antialiased=True)

    plt.scatter(
        xaxis,
        yaxis,
        marker="o",
        color=c_map,
        s=2
    )


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='slice_diagrams', description='Plot a slice of a color space.')
    parser.add_argument('--space', '-s', help='Desired space.')
    parser.add_argument('--gamut', '-g', default="srgb", help='Gamut to evaluate the color in (default is sRGB).')
    parser.add_argument('--constant', '-c', help="The channel to hold constant and the value to use 'name:value'.")
    parser.add_argument('--xaxis', '-x', help="The channel to plot on X axis 'name:range:offset'.")
    parser.add_argument('--yaxis', '-y', help="The channel to plot on Y axis 'name:range:offset'.")
    parser.add_argument('--polar', '-p', action="store_true", help="Graph the cylindrical space in polar coordinates.")
    parser.add_argument('--resolution', '-r', default="800", help="How densely to render the figure.")
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument(
        '--sub-title', default='', help="Provide a subtitle, if none is provided, will show contant channel."
    )
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')

    args = parser.parse_args()

    plot_slice(
        args.space,
        args.constant,
        args.xaxis,
        args.yaxis,
        gamut=args.gamut,
        resolution=int(args.resolution),
        title=args.title,
        subtitle=args.sub_title,
        dark=args.dark,
        polar=args.polar
    )

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
