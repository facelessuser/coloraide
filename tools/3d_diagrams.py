"""
Render 3D plots of sRGB in other color spaces.

In order to render things fast and allow for reasonable
performance, we render the outer shell of the space.

Only sRGB and related sRGB cylindrical models are precise,
all others are approximations of the shape due to our
approach.
"""
import itertools
import matplotlib.pyplot as plt
import sys
import os
import math
import argparse

sys.path.insert(0, os.getcwd())

from coloraide import Color  # noqa: E402
from coloraide.spaces import Cylindrical, Lchish, Labish  # noqa: E402
from coloraide.util import is_nan  # noqa: E402

axis_map = {
    # Lab like spaces
    "lab": [1, 2, 0],
    "lab-d65": [1, 2, 0],
    "oklab": [1, 2, 0],
    "jzazbz": [1, 2, 0],
    "ictcp": [1, 2, 0],
    "din99o": [1, 2, 0],
    "luv": [1, 2, 0],
    "luv-d65": [1, 2, 0],

    # Lch like spaces
    "lch": [2, 1, 0],
    "lch-d65": [2, 1, 0],
    "oklch": [2, 1, 0],
    "jzczhz": [2, 1, 0],
    "lch99o": [2, 1, 0],
    "lchuv": [2, 1, 0],
    "lchuv-d65": [2, 1, 0]
}


def add_color(space, color, x, y, z, c):
    """Add color to the provided arrays."""

    coords = color.convert(space).coords()
    x.append(coords[0])
    y.append(coords[1])
    z.append(coords[2])
    s = color.to_string(hex=True)
    c.append(s)


def add_cyl_color(space, color, x, y, z, c):
    """
    Add color to the provided arrays.

    Handles cylindrical spaces. Returns x (hue), y (chroma/saturation), z (value/lightness).
    """

    cyl = color.convert(space)

    chroma = cyl.chroma
    lightness = cyl.lightness
    hue = cyl.hue

    if is_nan(hue):
        hue = 0

    z.append(chroma * math.sin(math.radians(hue)))
    y.append(chroma * math.cos(math.radians(hue)))
    x.append(lightness)

    s = color.convert('srgb').to_string(hex=True)
    c.append(s)


def render_cart_space(space, resolution, data, c):
    """Render the space with the given resolution and factor."""

    x, y, z = data

    # We are rendering the spaces using sRGB, so just do a shell by picking
    # all the colors on the outside of the sRGB space. Render will be hollow.
    color = Color('srgb', [])
    for c1, c2 in itertools.product(
        (x / resolution for x in range(0, resolution + 1)),
        (x / resolution for x in range(0, resolution + 1))
    ):

        add_color(space, color.update('srgb', [0, c1, c2]), x, y, z, c)
        add_color(space, color.update('srgb', [1, c1, c2]), x, y, z, c)

        add_color(space, color.update('srgb', [c1, 0, c2]), x, y, z, c)
        add_color(space, color.update('srgb', [c1, 1, c2]), x, y, z, c)

        add_color(space, color.update('srgb', [c1, c2, 0]), x, y, z, c)
        add_color(space, color.update('srgb', [c1, c2, 1]), x, y, z, c)


def render_cyl_space(space, resolution, data, c):
    """
    Render the space with the given resolution and factor.

    The sRGB gamut is used for the plot. The HSV space is used as it maps
    far better to cylinder spaces. Very close to black, on some spaces the
    models don't cover very well, so we make an additional pass using
    Cartesian coordinates extremely close to black.

    It can be noted, we don't bother plotting anything from the bottom
    disc of the HSV cylinder as they all resolve to pure black. It generates
    a lot of redundant points.
    """

    x, y, z = data

    # Resolution increase in non-hue channels helps smooth out some spaces a bit more.
    res2 = int(resolution * 1.5)

    color = Color('srgb', [])
    is_labish = issubclass(Color.CS_MAP[space], Labish)
    add = add_color if is_labish else add_cyl_color

    # We are rendering the spaces using sRGB, so just do a shell by picking
    # all the colors on the outside of the sRGB space. Render will be hollow.
    for c1, c2 in itertools.product(
        ((x / resolution) * 360 for x in range(0, resolution + 1)),
        ((x / res2) for x in range(0, res2 + 1))
    ):

        # Only the top disc provides useful points, everything in the bottom just yields black.
        add(space, color.update('hsv', [c1, c2, 1]), x, y, z, c)
        add(space, color.update('hsv', [c1, 1, c2]), x, y, z, c)
        add(space, color.update('hsv', [c1, 1, c2 * 0.005]), x, y, z, c)


def render_srgb_cyl_space(space, resolution, factor, data, c):
    """
    Render the sRGB cylindrical space: HSL, HSV, HWB, etc.

    Will render cylinder with the caps on the top and bottom.
    """

    x, y, z = data
    factor = 100 if space in ('hsluv',) else 1

    # Render the cylinder by iterating through the hues and mapping them at the farthest
    # point from the center creating a hollow cylinder. Also, render the top and bottom disc caps.
    color = Color("srgb", [])
    for c1, t in itertools.product(
        ((x / resolution) * 360 for x in range(0, resolution + 1)),
        (((x / resolution) * factor, i) for i, x in enumerate(range(0, resolution + 1), 0))
    ):

        # Offset the plot on every other iteration blend the rows into a mesh
        # Better looking when low resolution zoomed into higher resolution
        c2, count = t
        if count % 2 and c1 < 360:
            c1 += (360 / resolution) * 0.5

        # Top disc
        x.append(c2 * math.sin(math.radians(c1)))
        y.append(c2 * math.cos(math.radians(c1)))
        z.append(factor)
        c.append(color.update(space, [c1, c2, factor]).to_string(hex=True))

        # Bottom disc
        x.append(c2 * math.sin(math.radians(c1)))
        y.append(c2 * math.cos(math.radians(c1)))
        z.append(0)
        c.append(color.update(space, [c1, c2, 0]).to_string(hex=True))

        # Cylinder portion
        x.append(factor * math.sin(math.radians(c1)))
        y.append(factor * math.cos(math.radians(c1)))
        z.append(c2)
        c.append(color.update(space, [c1, factor, c2]).to_string(hex=True))


def plot_space_in_srgb(space, title="", dark=False, resolution=70, rotate_elev=30.0, rotate_azim=-60.0):
    """Plot the given space in sRGB."""

    data = [[], [], []]
    c = []

    # Get names for
    names = Color.CS_MAP[space].CHANNEL_NAMES
    is_cyl = issubclass(Color.CS_MAP[space], Cylindrical)
    is_labish = issubclass(Color.CS_MAP[space], Labish)
    is_srgb_cyl = is_cyl and not issubclass(Color.CS_MAP[space], Lchish)

    # Some spaces need us to rearrange the order of the data
    axm = axis_map.get(space, [0, 1, 2])

    # Select the right theme
    if dark:
        plt.style.use('dark_background')
    else:
        plt.style.use('seaborn-bright')

    # Setup figure and axis
    figure = plt.figure()
    plt.tight_layout()
    ax = plt.axes(
        projection='3d',
        xlabel=names[axm[0]] if not is_cyl else "{} (0˚ - 360˚)".format(names[axm[0]]),
        ylabel=names[axm[1]],
        zlabel=names[axm[2]]
    )

    # Turn off ticks for cylindrical hue
    if is_cyl:
        ax.xaxis.set_ticks([])
    figure.add_axes(ax)

    # Add title
    plt.title(title if title else 'srgb rendered in {}'.format(space), pad=20)

    # Render the space
    if is_srgb_cyl:
        # Render a sRGB cylinder style plot
        render_srgb_cyl_space(space, resolution, 1, data, c)
    elif is_labish or is_cyl:
        # Render cylindrical spaces. Lab like spaces are cylindrical,
        # just represented in the Cartesian coordinate system.
        render_cyl_space(space, resolution, data, c)
    else:
        # Render Cartesian spaces.
        # These are rectangular spaces like RGB spaces and XYZ.
        render_cart_space(space, resolution, data, c)

    # Setup the aspect ratio
    ax.set_box_aspect((1, 1, 1))

    # Plot the data
    ax.scatter3D(data[axm[0]], data[axm[1]], data[axm[2]], c=c, s=20 * 4)
    ax.view_init(rotate_elev, rotate_azim)


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='3d_diagrams', description='Plot 3D sRGB in different color spaces.')
    parser.add_argument('--space', '-s', help='Desired space.')
    parser.add_argument(
        '--resolution', '-r',
        default="200",
        help=(
            "How densely to render the figure. Some spaces need higher resolution to flesh out certain areas, "
            "but it comes at the cost of speed."
        )
    )
    parser.add_argument('--rotate-elev', '-e', default=30.0, type=float, help="Rotate x axis by specified angle.")
    parser.add_argument('--rotate-azim', '-a', default=-60.0, type=float, help="Rotate y axis by specified angle.")
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    args = parser.parse_args()

    plot_space_in_srgb(
        args.space,
        title=args.title,
        dark=args.dark,
        resolution=int(args.resolution),
        rotate_elev=args.rotate_elev,
        rotate_azim=args.rotate_azim
    )

    if args.output:
        plt.savefig(args.output, dpi=200)
    else:
        plt.gcf().set_dpi(200)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
