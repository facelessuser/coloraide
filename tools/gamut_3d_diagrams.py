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

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide.spaces import Cylindrical, LChish, Labish  # noqa: E402
from coloraide.algebra import is_nan  # noqa: E402

# Special cases for certain color spaces
color_options = {
    'hsluv': {'factor': 100, 'chroma': 's', 'force_top': True, 'force_bottom': True, 'is_hsl': True},
    'hpluv': {'factor': 100, 'chroma': 'p', 'force_top': True, 'force_bottom': True, 'is_hsl': True},
    'hsl': {'chroma': 's', 'force_top': True, 'force_bottom': True},
    'okhsl': {'chroma': 's', 'force_top': True, 'force_bottom': True, "is_hsl": True},
    'hsv': {'chroma': 's', 'lightness': 'v', 'force_bottom': True, 'is_hsv': True},
    'okhsv': {'chroma': 's', 'lightness': 'v', 'force_bottom': True, 'is_hsv': True},
    'hsi': {'chroma': 's', 'lightness': 'i', 'force_bottom': True},
    'hwb': {'chroma': 'w', 'lightness': 'b', 'force_max_radius': True, 'force_top': True, 'force_bottom': True},
    'cam16-jmh': {'chroma': 'm'}
}


def create_custom_hsv(space, gamut, is_hsl=False, factor=1):
    """Create a custom color object that has access to special `hsv-gamut` space to map surface in."""

    cs = Color.CS_MAP[space]

    if is_hsl:
        # Create a custom HSV space based off the HSL space
        class HSV(type(Color.CS_MAP['hsv'])):
            NAME = 'hsv-{}'.format(gamut)
            BASE = space
            GAMUT_CHECK = cs.GAMUT_CHECK
            WHITE = cs.WHITE
            DYAMIC_RANGE = cs.DYNAMIC_RANGE

            def to_base(self, coords):
                """To HSL from HSV."""

                coords = super().to_base(coords)
                return [coords[0], coords[1] * factor, coords[2] * factor]

            def from_base(self, coords):
                """From HSL to HSV."""

                return super().from_base([coords[0], coords[1] / factor, coords[2] / factor])

        class ColorCyl(Color):
            """Custom color."""

        ColorCyl.register(HSV())
    else:
        # Create custom cylindrical spaces based on the specified gamut
        class HSV(type(Color.CS_MAP['hsv'])):
            NAME = 'hsv-{}'.format(gamut)
            BASE = 'hsl-{}'.format(gamut)
            GAMUT_CHECK = gamut
            WHITE = cs.WHITE
            DYAMIC_RANGE = cs.DYNAMIC_RANGE

        class HSL(type(Color.CS_MAP['hsl'])):
            NAME = 'hsl-{}'.format(gamut)
            BASE = gamut
            GAMUT_CHECK = gamut
            WHITE = cs.WHITE
            DYAMIC_RANGE = cs.DYNAMIC_RANGE

        class ColorCyl(Color):
            """Custom color."""

        ColorCyl.register([HSV(), HSL()])

    return ColorCyl


def add_rect_color(space, color, x, y, z, c):
    """Add rectangular color to the provided arrays."""

    coords = color.convert(space)[:-1]
    x.append(coords[0])
    y.append(coords[1])
    z.append(coords[2])
    if not color.in_gamut():
        m = max(color[:-1])
        color.update('srgb', [(i / m if m != 0 else 0) for i in color[:-1]], color[-1])
    c.append(color.to_string(hex=True))


def add_lab_color(space, color, x, y, z, c):
    """Add Lab like color to the provided arrays."""

    coords = color.convert(space)[:-1]
    x.append(coords[1])
    y.append(coords[2])
    z.append(coords[0])
    if not color.in_gamut():
        m = max(color[:-1])
        color.update('srgb', [(i / m if m != 0 else 0) for i in color[:-1]], color[-1])
    c.append(color.to_string(hex=True))


def add_cyl_color(space, color, x, y, z, c):
    """
    Add color to the provided arrays.

    Handles cylindrical spaces. Returns x (hue), y (chroma/saturation), z (value/lightness).
    """

    cyl = color.convert(space)
    lightness = cyl.get(color_options.get(space, {}).get('lightness', 'lightness'))
    chroma = cyl.get(color_options.get(space, {}).get('chroma', 'chroma'))
    hue = cyl.get(color_options.get(space, {}).get('hue', 'hue'))

    if is_nan(hue):
        hue = cyl._space.achromatic_hue()

    x.append(chroma * math.sin(math.radians(hue)))
    y.append(chroma * math.cos(math.radians(hue)))
    z.append(lightness)

    s = color.convert('srgb')
    if not color.in_gamut():
        m = max(s[:-1])
        s.update('srgb', [(i / m if m != 0 else 0) for i in s[:-1]], s[-1])
    c.append(s.to_string(hex=True))


def render_space(space, gamut, resolution, factor, x, y, z, c):
    """
    Render the space with the given resolution and factor.

    Any normal RGB gamut can be used, assuming it has ranges [0,1].
    The HSV space is used as to map though as it generally maps creates
    better color shells for most spaces.

    Very close to black on some spaces the models doesn't cover quite as
    well, so we make an additional pass at a higher resolution very close
    to black.

    There are a number of special options to handle RGB cylinder spaces.
    Some require us to generate top and bottom caps, some require us to
    force a max radius. This is mainly because these models are special
    and don't quite fit generically with things like Lab, LCh, and rectangular
    spaces.
    """

    is_hsv = color_options.get(space, {}).get('is_hsv', False)
    is_hsl = color_options.get(space, {}).get('is_hsl', False)
    if not is_hsv:
        ColorCyl = create_custom_hsv(space, gamut, is_hsl, factor)
        gamut_space = 'hsv-{}'.format(gamut)
    else:
        ColorCyl = Color
        gamut_space = space

    # Resolution increase in non-hue channels helps smooth out some spaces a bit more.
    res2 = int(resolution * 1.5)

    color = ColorCyl('srgb', [])
    is_cyl = isinstance(ColorCyl.CS_MAP[space], Cylindrical)
    is_labish = isinstance(ColorCyl.CS_MAP[space], Labish)
    is_lchish = isinstance(ColorCyl.CS_MAP[space], LChish)
    if is_labish:
        add = add_lab_color
    elif not is_cyl:
        add = add_rect_color
    else:
        add = add_cyl_color
    force_max_radius = not is_lchish and is_cyl and color_options.get(space, {}).get('force_max_radius', False)
    force_bottom = color_options.get(space, {}).get('force_bottom', False)
    force_top = color_options.get(space, {}).get('force_top', False)

    # We are rendering the spaces using sRGB, so just do a shell by picking
    # all the colors on the outside of the sRGB space. Render will be hollow.
    for c1, t in itertools.product(
        ((x / resolution) * 360 for x in range(0, resolution + 1)),
        (((x / res2), i) for i, x in enumerate(range(0, res2 + 1), 0)),
    ):

        # Offset the plot on every other iteration blend the rows into a mesh
        # Better looking when low resolution zoomed into higher resolution
        c2, count = t
        if is_cyl:
            if count % 2 and c1 < 360:
                c1 += (360 / resolution) * 0.5

        if not force_max_radius:
            add(space, color.update(gamut_space, [c1, c2, 1]), x, y, z, c)
            add(space, color.update(gamut_space, [c1, 1, c2]), x, y, z, c)
        else:
            # Certain color spaces, like HWB, we must force max radius as the space
            # is constructed in a way that just doesn't translate to how we map other spaces.
            x.append(factor * math.sin(math.radians(c1)))
            y.append(factor * math.cos(math.radians(c1)))
            z.append(c2)
            c.append(color.update(space, [c1, factor, c2]).to_string(hex=True))

        if not is_lchish and is_cyl:
            # RGB cylinders often map max lightness to a single point instead of rendering a full cylinder
            # top an bottom. The alternative is to map the radius with a magnitude that lessens as we approach
            # achromatic, or just render the top and bottom of the cylinder with a disc. We've chosen the latter.
            # Some cylinder spaces, like HSV, do not require a top.

            if force_top:
                # Top disc
                x.append(c2 * factor * math.sin(math.radians(c1)))
                y.append(c2 * factor * math.cos(math.radians(c1)))
                z.append(factor)
                c.append(color.update(space, [c1, c2, factor]).to_string(hex=True))

            if force_bottom:
                # Bottom disc
                x.append(c2 * factor * math.sin(math.radians(c1)))
                y.append(c2 * factor * math.cos(math.radians(c1)))
                z.append(0)
                c.append(color.update(space, [c1, c2 * factor, 0]).to_string(hex=True))
        else:
            # Some spaces require a higher resolution in the black region to fill in any holes
            add(space, color.update(gamut_space, [c1, 1, c2 * 0.005]), x, y, z, c)


def plot_gamut_in_space(space, gamut, title="", dark=False, resolution=70, rotate_elev=30.0, rotate_azim=-60.0):
    """Plot the given space in sRGB."""

    data = [[], [], []]
    c = []

    # Get names for
    target = Color.CS_MAP[space]
    names = target.CHANNELS
    is_cyl = isinstance(target, Cylindrical)
    is_labish = isinstance(target, Labish)
    is_lchish = isinstance(target, LChish)

    if not is_lchish and is_cyl:
        g = Color.CS_MAP[space].GAMUT_CHECK
        if g is not None:
            gamut = g

    # Some spaces need us to rearrange the order of the data
    if is_labish:
        c1, c2, c3 = target.labish_indexes()
        axm = [c2, c3, c1]
    elif is_lchish:
        c1, c2, c3 = target.lchish_indexes()
        axm = [c3, c2, c1]
    elif is_cyl:
        axm = [0, 1, 2]
    else:
        axm = color_options.get(space, {}).get('axis', [0, 1, 2])

    factor = color_options.get(space, {}).get('factor', 1)

    # Select the right theme
    if dark:
        plt.style.use('dark_background')
    else:
        plt.style.use('seaborn-v0_8-bright')

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
    plt.title(title if title else "'{}' Rendered in '{}'".format(gamut, space), pad=20)

    # Render the space
    render_space(space, gamut, resolution, factor, data[axm[0]], data[axm[1]], data[axm[2]], c)

    # Setup the aspect ratio
    ax.set_box_aspect((1, 1, 1))

    # Plot the data
    ax.scatter3D(data[axm[0]], data[axm[1]], data[axm[2]], c=c, s=20 * 4)
    ax.view_init(rotate_elev, rotate_azim)


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='3d_diagrams', description='Plot 3D gamut in a different color spaces.')
    parser.add_argument('--space', '-s', help='Desired space.')
    parser.add_argument(
        '--gamut',
        '-g',
        default='srgb',
        help=(
            'Gamut space to render space in. Gamut space must be bounded and must have channels in the range [0, 1].'
            'As only a shell is rendered for the gamut, the target space should be less than or equal to the size of '
            'the target gamut or there will be areas that do not render. Cylindrical spaces based specifically off '
            'an RGB gamut, such as HSL being based on sRGB, will only be done under the related gamut and will ignore '
            'this option.'
        )
    )
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
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    args = parser.parse_args()

    plot_gamut_in_space(
        args.space,
        args.gamut,
        title=args.title,
        dark=args.dark,
        resolution=int(args.resolution),
        rotate_elev=args.rotate_elev,
        rotate_azim=args.rotate_azim
    )

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
