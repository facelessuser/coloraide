"""
Model interpolation in a 3D space.

Interpolation can be done in any space, but displaying is currently only allowed in non polar spaces.
"""
import sys
import os
import matplotlib.pyplot as plt
import argparse

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide.spaces import Cylindrical  # noqa: E402


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='interp_3d_diagram', description='Demonstrate interpolation in 3D.')
    parser.add_argument('--space', '-s', default='srgb', help="Space to interpolate in.")
    parser.add_argument('--color', '-c', action='append', help="Color.")
    parser.add_argument('--display', '-d', help="Display space.")
    parser.add_argument('--method', '-m', default='linear', help="Interplation method to use: linear, bezier, etc.")
    parser.add_argument('--extrapolate', '-e', action='store_true', help='Extrapolate values.')
    parser.add_argument('--title', '-T', default='', help="Provide a title for the diagram.")
    parser.add_argument('--subtitle', '-t', default='', help="Provide a subtitle for the diagram.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    args = parser.parse_args()

    if args.dark:
        edge = 'black'
        line = '#333333'
        plt.style.use('dark_background')
    else:
        edge = 'black'
        line = '#333333'
        plt.style.use('seaborn-v0_8-bright')

    # Create the color points
    x = []
    y = []
    z = []
    c = []
    colors = []
    display = None
    d = args.space if args.display is None else args.display
    for color in args.color:
        current = Color(color).convert(args.space)
        display = current.convert(d)
        x.append(display[0])
        y.append(display[1])
        z.append(display[2])
        c.append(current.convert('srgb').to_string(hex=True))
        colors.append(current)

    # We don't have logic to handle cylindrical color spaces.
    if isinstance(display._space, Cylindrical):
        raise ValueError('Displaying interpolation in a cylindrical color space is not currently supported.')

    # Setup figure and axis
    figure = plt.figure()
    plt.tight_layout()
    ax = plt.axes(
        projection='3d',
        xlabel=display._space.CHANNELS[0],
        ylabel=display._space.CHANNELS[1],
        zlabel=display._space.CHANNELS[2]
    )

    # Create title
    if not args.title:
        title = "{} Interpolation in '{}' space displayed in the '{}' space.".format(
            args.method.title(), args.space, args.display
        )
    else:
        title = args.title
    plt.suptitle(title)

    # Add axis to figure
    figure.add_axes(ax)

    # Interpolate between the entire range and optionally extrapolate
    i = Color.interpolate(
        colors,
        space=args.space,
        out_space=args.display,
        method=args.method,
        extrapolate=args.extrapolate
    )
    points = []
    if not args.extrapolate:
        offset, factor = 0, 1
    else:
        offset, factor = 1, 3
    for r in range(1001):
        points.append(i((r * factor / 1000) - offset)[:-1])

    # Plot the interpolation line and plot the colors.
    xs, ys, zs = list(zip(*points))
    ax.plot(xs, ys, zs, color=line)
    ax.scatter(x, y, z, c=c, s=20 * 4, edgecolors=edge)

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
