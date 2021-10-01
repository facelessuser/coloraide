"""
Render 3D plots of sRGB in other color spaces.

In order to render things fast and allow for reasonable
performance, we render the outer shell of the space.
"""
import itertools
import matplotlib.pyplot as plt
import sys
import os
import math
import argparse

sys.path.insert(0, os.getcwd())

from coloraide import Color  # noqa: E402
from coloraide.spaces import Cylindrical  # noqa: E402
from coloraide.util import is_nan  # noqa: E402

UNSUPPORTED = """Rendering of '{}' is not officially supported.
Cylindrical spaces will, at their best, will be mislabeled and
rendered as their cartesian counter part. At worst, they will be
incomplete and/or distored.
"""


def add_srgb_color(space, color, x, y, z, c):
    """Add color to the provided arrays."""

    coords = color.convert(space).coords()
    x.append(coords[0])
    y.append(coords[1])
    z.append(coords[2])
    s = color.to_string(hex=True)
    c.append(s)


def add_srgb_color_cyl(space, color, x, y, z, c):
    """Add color to the provided arrays."""

    cyl = color.convert(space)
    c1 = None
    c2 = None

    # Cylindrical spaces we support usually have
    # two of the below attributes.
    for attr in ('saturation', 'chroma', 'whiteness'):
        if hasattr(cyl, attr):
            c1 = getattr(cyl, attr)
            break
    for attr in ('lightness', 'value', 'blackness'):
        if hasattr(cyl, attr):
            c2 = getattr(cyl, attr)
            break
    hue = cyl.hue
    if is_nan(hue):
        hue = 0

    x.append(c1 * math.sin(math.radians(hue)))
    y.append(c1 * math.cos(math.radians(hue)))
    z.append(c2)
    s = color.convert('srgb').to_string(hex=True)
    c.append(s)


def render_space(space, add, resolution, factor, x, y, z, c):
    """Render the space with the given resolution and factor."""

    for c1, c2 in itertools.product(
        ((x / resolution) * factor for x in range(0, resolution + 1)),
        ((x / resolution) * factor for x in range(0, resolution + 1))
    ):

        add(space, Color('srgb', [0, c1, c2]), x, y, z, c)
        add(space, Color('srgb', [1, c1, c2]), x, y, z, c)

        add(space, Color('srgb', [c1, 0, c2]), x, y, z, c)
        add(space, Color('srgb', [c1, 1, c2]), x, y, z, c)

        add(space, Color('srgb', [c1, c2, 0]), x, y, z, c)
        add(space, Color('srgb', [c1, c2, 1]), x, y, z, c)


def plot_space_in_srgb(space, dark=False, resolution=70):
    """Plot the given space in sRGB."""

    x = []
    y = []
    z = []
    c = []

    names = Color.CS_MAP[space].CHANNEL_NAMES
    is_cyl = issubclass(Color.CS_MAP[space], Cylindrical)

    if is_cyl:
        print(UNSUPPORTED.format(space))

    add = add_srgb_color if not is_cyl else add_srgb_color_cyl

    if dark:
        plt.style.use('dark_background')
    else:
        plt.style.use('seaborn-whitegrid')

    figure = plt.figure()
    ax = plt.axes(
        projection='3d',
        xlabel=names[0],
        ylabel=names[1],
        zlabel=names[2]
    )
    figure.add_axes(ax)
    plt.title('srgb rendered in {}'.format(space), pad=20)

    render_space(space, add, resolution, 1, x, y, z, c)

    # Oklab needs much higher resolution near black
    if space in ('oklab', 'oklch'):
        render_space(space, add, resolution // 2, 0.0124, x, y, z, c)
    # ICtCp needs an absurd amount of resolution near black
    elif space == 'ictcp':
        render_space(space, add, resolution, 0.3, x, y, z, c)
        render_space(space, add, resolution, 0.1, x, y, z, c)
        render_space(space, add, resolution, 0.03, x, y, z, c)

    ax.scatter3D(x, y, z, c=c)


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='3d_diagrams', description='Plot 3D sRGB in different color spaces.')
    parser.add_argument('--space', '-s', help='Desired space.')
    parser.add_argument(
        '--resolution', '-r',
        default="70",
        help=(
            "How densely to render the figure. Some spaces need higher resolution to flesh out certain areas, "
            "but it comes at the cost of speed."
        )
    )
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    args = parser.parse_args()

    plot_space_in_srgb(
        args.space,
        dark=args.dark,
        resolution=int(args.resolution)
    )

    if args.output:
        plt.savefig(args.output)
    else:
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
