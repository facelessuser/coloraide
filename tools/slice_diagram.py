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
from shapely.geometry import Polygon
from shapely.geometry.base import dump_coords
from shapely.geometry.collection import GeometryCollection
from shapely.geometry.linestring import LineString

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide import NaN  # noqa: E402
from coloraide.util import fmt_float  # noqa: E402
from coloraide.spaces import Cylindrical  # noqa: E402


def needs_workaround(color):
    """
    Check if LChuv has high chroma and no lightness.

    LChuv will have such values all in gamut and create weird graphs.
    This is just due to how LChuv algorithm handles high chroma and zero lightness,
    it all gets treated as black which is in gamut for almost any color.
    """

    return (
        color.space().startswith(('lchuv', 'cam16-jmh', 'hct')) and
        color['lightness'] == 0 and
        not color.normalize().is_nan('hue')
    )


def plot_slice(
    space,
    constants,
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
        plt.style.use('seaborn-v0_8-darkgrid')
        default_color = 'black'
    else:
        plt.style.use('dark_background')
        default_color = 'white'

    figure = plt.figure()

    # Create a color object based on the specified space.
    c = Color(space, [])

    # Parse the channel strings into actual values
    chan_constants = []
    for chan in constants.split(';'):
        n, v = [
            c if i == 0 else float(c if c != 'none' else 'nan') for i, c in enumerate(chan.split(':'), 0)
        ]
        n = c._space.CHANNEL_ALIASES.get(n, n)
        i = c._space.get_channel_index(n)
        chan_constants.append((n, v, i))

    name1, start1, end1 = [
        c if i == 0 else float(c) for i, c in enumerate(channel1.split(':'), 0)
    ]
    factor1 = abs(start1 - end1) if end1 < 0 else (end1 - start1)
    offset1 = start1

    name2, start2, end2 = [
        c if i == 0 else float(c) for i, c in enumerate(channel2.split(':'), 0)
    ]
    factor2 = abs(start2 - end2) if end2 < 0 else (end2 - start2)
    offset2 = start2

    # Get the actual indexes of the specified channels
    name1 = c._space.CHANNEL_ALIASES.get(name1, name1)
    index1 = c._space.get_channel_index(name1)
    name2 = c._space.CHANNEL_ALIASES.get(name2, name2)
    index2 = c._space.get_channel_index(name2)
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
    # This is done from the perspective of the X and Y axis.
    # We will capture the min and max Y for a given X and
    # the min and max X for a given Y.
    # Both are imperfect, but taking both and find the
    # the intersection should yield a suitable edge.
    edge_map_x = {}
    edge_map_y = {}
    ex = []
    ey = []

    # Iterate through the two specified channels
    for c1, c2 in itertools.product(
        ((x / res * factor1) + offset1 for x in range(0, res + 1)),
        ((x / res * factor2) + offset2 for x in range(0, res + 1))
    ):
        # Set the appropriate channels and update the color object
        coords = [NaN] * (2 + len(chan_constants))
        for chan in chan_constants:
            coords[chan[2]] = chan[1]
        coords[index1] = c1
        coords[index2] = c2
        c.update(space, coords)

        # Only process colors within the gamut of sRGB.
        if c.in_gamut(gamut, tolerance=0) and not needs_workaround(c):
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
            # This should be all we need for polar.
            if c1 not in edge_map_x:
                mn = mx = c2
            else:
                mn, mx = edge_map_x[c1]
                if c2 < mn:
                    mn = c2
                elif c2 > mx:
                    mx = c2
            edge_map_x[c1] = [mn, mx]

            # If we aren't doing polar, we need both the X and Y perspective
            if hue_index == -1:
                if c2 not in edge_map_y:
                    mn = mx = c1
                else:
                    mn, mx = edge_map_y[c2]
                    if c1 < mn:
                        mn = c1
                    elif c1 > mx:
                        mx = c1
                edge_map_y[c2] = [mn, mx]

            # Save the points
            xaxis.append(c1)
            yaxis.append(c2)
            c_map.append(c.convert('srgb').to_string(hex=True))

    # Create axes
    ax = plt.axes(
        xlabel='{}: {} - {}'.format(name1, fmt_float(c1_mn, 5), fmt_float(c1_mx, 5)),
        ylabel='{}: {} - {}'.format(name2, fmt_float(c2_mn, 5), fmt_float(c2_mx, 5)),
        **kwargs
    )

    # Create titles
    if not title:
        title = "Plot of {} showing '{}' and '{}': {}".format(
            space, name1, name2, ' '.join(['{} = {}'.format(chan[0], fmt_float(chan[1], 5)) for chan in chan_constants])
        )

    plt.suptitle(title)
    if subtitle:
        if hue_index == -1:
            ax.set_title(subtitle, fontdict={'fontsize': 8})
        else:
            ax.set_title(subtitle, fontdict={'fontsize': 8}, pad=2)

    # Set aspect
    ax.set_aspect('auto' if hue_index == -1 else 'equal')
    figure.add_axes(ax)

    # Fill colors
    plt.scatter(
        xaxis,
        yaxis,
        marker="o",
        color=c_map,
        s=2
    )

    # Create a border from the X axis perspective
    edge_x = []
    temp = []
    for p1, edges in edge_map_x.items():
        if hue_index == -1:
            # Min and max
            edge_x.append((p1, edges[0]))
            temp.append((p1, edges[1]))
        else:
            # Just need max for polar
            edge_x.append((p1, edges[1]))

    if hue_index == -1:
        # Combine the min/max values in one shape
        edge_x.extend(reversed(temp))
        # Close shape
        edge_x.append(edge_x[0])

    # Create a border from the Y axis perspective
    if hue_index == -1:
        edge_y = []
        temp.clear()

        for p1 in sorted(edge_map_y.keys()):
            edges = edge_map_y[p1]
            edge_y.append((edges[0], p1))
            temp.append((edges[1], p1))

        edge_y.extend(reversed(temp))
        edge_y.append(edge_y[0])

        # Get the intersection of X and Y to get the most accurate border
        poly = Polygon(edge_x).intersection(Polygon(edge_y))
        if isinstance(poly, GeometryCollection):
            for a in poly.geoms:
                # Sometimes the intersection can have weird, unnecessary `LineString`.
                # This occurs with very complex polygons. Just throw them away until
                # as they seem to be a bug.
                if isinstance(a, LineString):
                    continue
                ex, ey = zip(*dump_coords(a))
        else:
            ex, ey = zip(*dump_coords(poly))
    else:
        # Using polar, so just split the data by axis
        ex, ey = zip(*edge_x)

    # Plot the edge border
    plt.plot(ex, ey, color=default_color, marker="", linewidth=2, markersize=0, antialiased=True)


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='slice_diagrams', description='Plot a slice of a color space.')
    parser.add_argument('--space', '-s', help='Desired space.')
    parser.add_argument('--gamut', '-g', default="srgb", help='Gamut to evaluate the color in (default is sRGB).')
    parser.add_argument(
        '--constant', '-c', help="The channel(s) to hold constant and the value to use 'name:value;name2:value2'."
    )
    parser.add_argument('--xaxis', '-x', help="The channel to plot on X axis 'name:min:max'.")
    parser.add_argument('--yaxis', '-y', help="The channel to plot on Y axis 'name:min:max'.")
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
