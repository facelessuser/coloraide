"""
Render 3D plots of sRGB in other color spaces.

In order to render things fast and allow for reasonable
performance, we render the outer shell of the space.

Only sRGB and related sRGB cylindrical models are precise,
all others are approximations of the shape due to our
approach.
"""
import matplotlib.pyplot as plt
import sys
import os
import argparse
import numpy as np

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide.spaces import Cylindrical, LChish, Labish, HSLish, HSVish  # noqa: E402
from coloraide import algebra as alg  # noqa: E402

# Special cases for certain color spaces
color_options = {
    'hpluv': {'gamut_self': True, 'factor': 100},
    'hwb': {'gamut_self': True, 'zsort': 'max'}
}


def create_custom_hsl(gamut):
    """Create a custom color object that has access to special `hsl-gamut` space to map surface in."""

    cs = Color.CS_MAP[gamut]

    class HSL(type(Color.CS_MAP['hsl'])):
        NAME = 'hsl-{}'.format(gamut)
        BASE = gamut
        GAMUT_CHECK = gamut
        WHITE = cs.WHITE
        DYAMIC_RANGE = cs.DYNAMIC_RANGE

    class ColorCyl(Color):
        """Custom color."""

    ColorCyl.register(HSL())

    return ColorCyl


def cyl_disc(ColorCyl, space, gamut, factor, location, mode, x, y, z, cmap, resolution, opacity):
    """Plot cylindrical disc."""

    cs = ColorCyl.CS_MAP[space]
    if isinstance(cs, (HSVish, HSLish)):
        space_type = 'hslish/hsvish'
    else:
        space_type = space

    b = 0.0 if location == 'bottom' else 1.0 * factor
    start, end = (1.0 * factor, 0.0) if location == 'bottom' else (0.0, 1.0 * factor)

    # Simple style, just create a dot in the center to complete the mesh
    if mode == 'simple':
        c = ColorCyl(gamut, [0, 0, b], opacity).convert(space, norm=False)
        if space_type == 'hslish/hsvish':
            hue, saturation, lightness = c._space.indexes()
            a, b = alg.polar_to_rect(c[saturation], c[hue])
            x.append([a] * resolution)
            y.append([b] * resolution)
            z.append([c[lightness]] * resolution)
        else:
            hue = c._space.hue_index()
            a, b = alg.polar_to_rect(c[1], c[hue])
            x.append([a] * resolution)
            y.append([b] * resolution)
            z.append([c[2]] * resolution)
        s = c.convert('srgb')
        if not s.in_gamut():
            s.fit()
        cmap.append([s.to_string(hex=True)] * resolution)
        return

    # Create concentric circles
    c1 = ColorCyl(gamut, [0, start, b], opacity)
    c2 = ColorCyl(gamut, [359.99999, start, b], opacity)
    s1 = ColorCyl.steps([c1, c2], steps=resolution, space=gamut, hue='specified')
    s2 = [c.clone().set('w', end) for c in s1]

    step = int(resolution / 2)
    for r in range(step + 1):
        if location == 'bottom':
            r = step - r
        x.append([])
        y.append([])
        z.append([])
        cmap.append([])
        for t1, t2 in zip(s1, s2):
            c = t1.mix(t2, r / step, space=gamut, hue='specified')
            c.convert(space, norm=False, in_place=True)
            if space_type == 'hslish/hsvish':
                hue, saturation, lightness = c._space.indexes()
                a, b = alg.polar_to_rect(c[saturation], c[hue])
                x[-1].append(a)
                y[-1].append(b)
                z[-1].append(c[lightness])
            else:
                hue = c._space.hue_index()
                a, b = alg.polar_to_rect(c[1], c[hue])
                x[-1].append(a)
                y[-1].append(b)
                z[-1].append(c[2])
            s = c.convert('srgb')
            if not s.in_gamut():
                s.fit()
            cmap[-1].append(s.to_string(hex=True))


def render_space(space, gamut, ax, mode, resolution, opacity):
    """
    Render the space with the given resolution and factor.

    Any normal RGB gamut can be used, assuming it has ranges [0,1].
    The HSL space is used to map as it makes it easy to get the outermost
    colors of RGB spaces.

    There are a number of special options to handle RGB cylinder spaces.
    Some require us to generate top and bottom caps. This is mainly because
    these models are special and don't quite fit generically with things like
    Lab, LCh, and rectangular spaces.
    """

    x = []
    y = []
    z = []
    cmap = []

    cs = Color.CS_MAP[space]

    # What kind of space are we dealing with?
    is_cyl = isinstance(cs, Cylindrical)
    if isinstance(cs, Labish):
        space_type = 'labish'
    elif isinstance(cs, LChish):
        space_type = 'lchish'
    elif isinstance(cs, HSVish):
        space_type = 'hsvish'
    elif isinstance(cs, HSLish):
        space_type = 'hslish'
    else:
        space_type = space

    # Create an HSL color space for the gamut for easily creating
    # a shell of the gamut. If we are rendering in sRGB gamut, we
    # can use the already present HSL space. Some spaces are special
    # and we must use themselves as the gamut, skip this step if
    # required.
    if color_options.get(space, {}).get('gamut_self'):
        ColorCyl = Color
        gamut_space = space
    elif gamut != 'srgb':
        ColorCyl = create_custom_hsl(gamut)
        gamut_space = 'hsl-{}'.format(gamut)
    else:
        ColorCyl = Color
        gamut_space = 'hsl'

    # Does the space require special factoring?
    factor = color_options.get(space, {}).get('factor', 1)

    # Calculate top disc
    if space_type in ('hslish', 'hwb'):
        cyl_disc(
            ColorCyl,
            space,
            gamut_space,
            factor,
            'top',
            'full' if space_type == 'hwb' else 'simple',
            x,
            y,
            z,
            cmap,
            resolution,
            opacity
        )

    # Calculate top cylinder
    c1 = ColorCyl(gamut_space, [0, 1 * factor, 1 * factor], opacity)
    c2 = ColorCyl(gamut_space, [0, 1 * factor, 0], opacity)
    c3 = ColorCyl(gamut_space, [359.99999, 1 * factor, 1 * factor], opacity)
    c4 = ColorCyl(gamut_space, [359.99999, 1 * factor, 0], opacity)
    s1 = ColorCyl.steps([c1, c2], steps=int(resolution / 2), space=gamut_space)
    s2 = ColorCyl.steps([c3, c4], steps=int(resolution / 2), space=gamut_space)

    for t1, t2 in zip(s1, s2):
        x.append([])
        y.append([])
        z.append([])
        cmap.append([])
        for c in ColorCyl.steps([t1, t2], steps=resolution, space=gamut_space, hue='specified'):
            c = c.convert(space, norm=False)

            if space_type in ('hslish', 'hsvish'):
                hue, saturation, lightness = c._space.indexes()
                a, b = alg.polar_to_rect(c[saturation], c[hue])
                x[-1].append(a)
                y[-1].append(b)
                z[-1].append(c[lightness])
            elif space_type == 'lchish':
                lightness, chroma, hue = c._space.indexes()
                a, b = alg.polar_to_rect(c[chroma], c[hue])
                x[-1].append(a)
                y[-1].append(b)
                z[-1].append(c[lightness])
            elif space_type == 'labish':
                lightness, a, b = c._space.indexes()
                x[-1].append(c[a])
                y[-1].append(c[b])
                z[-1].append(c[lightness])
            elif is_cyl:
                hue = c._space.hue_index()
                if hue == 0:
                    i, j = 1, 2
                elif hue == 1:
                    i, j = 0, 2
                else:
                    i, j = 0, 1
                a, b = alg.polar_to_rect(c[i], c[hue])
                x[-1].append(a)
                y[-1].append(b)
                z[-1].append(c[j])
            else:
                x[-1].append(c[0])
                y[-1].append(c[1])
                z[-1].append(c[2])

            s = c.convert('srgb')
            if not s.in_gamut():
                s.fit()
            cmap[-1].append(s.to_string(hex=True))

    # Calculate bottom disc
    if space_type in ('hslish', 'hsvish', 'hwb'):
        cyl_disc(
            ColorCyl,
            space,
            gamut_space,
            factor,
            'bottom',
            'full' if space_type == 'hwb' else 'simple',
            x,
            y,
            z,
            cmap,
            resolution,
            opacity
        )

    # Plot the data
    if mode == 'wireframe':
        ax.plot_wireframe(
            np.asarray(x), np.asarray(y), np.asarray(z),
            color=Color('blue').set('alpha', opacity).to_string(hex=True),
            rcount=resolution,
            ccount=resolution,
            antialiased=True
        )
    elif mode == 'scatter':
        scatter_cmap = []
        for m in cmap:
            scatter_cmap.extend(m)
        ax.scatter(
            np.asarray(x).ravel(), np.asarray(y).ravel(), np.asarray(z).ravel(),
            c=scatter_cmap,
            s=20 * 4
        )
    else:
        # Plot the data as a 3D surface.
        ax.plot_surface(
            np.asarray(x), np.asarray(y), np.asarray(z),
            rcount=resolution,
            ccount=resolution,
            zsort=color_options.get(space, {}).get('zsort', 'average'),
            facecolors=cmap,
            shade=False,
            antialiased=True,
        )


def plot_gamut_in_space(
    space,
    gamut,
    title="",
    dark=False,
    rotate_elev=30.0,
    rotate_azim=-60.0,
    mode='surface',
    resolution=200,
    opacity=1.0
):
    """Plot the given space in sRGB."""

    # Get names for
    target = Color.CS_MAP[space]
    names = target.CHANNELS
    is_cyl = isinstance(target, Cylindrical)
    is_labish = isinstance(target, Labish)
    is_lchish = isinstance(target, LChish)
    is_hslish_hsvish = isinstance(target, (HSLish, HSVish))

    # Some spaces need us to rearrange the order of the data
    if is_labish:
        c1, c2, c3 = target.indexes()
        axm = [c2, c3, c1]
    elif is_lchish:
        c1, c2, c3 = target.indexes()
        axm = [c3, c2, c1]
    elif is_hslish_hsvish:
        axm = [0, 1, 2]
    else:
        axm = [0, 1, 2]

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
    acutal_gamut = space if color_options.get(space, {}).get('gamut_self') else gamut
    plt.title(title if title else "'{}' Rendered in '{}'".format(acutal_gamut, space), pad=20)

    # Setup the aspect ratio
    ax.set_box_aspect((1, 1, 1))

    # Render the space
    render_space(space, gamut, ax, mode, resolution, opacity)

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
    parser.add_argument('--opacity', default=1.0, type=float, help="opacity")
    parser.add_argument('--render-mode', '-m', default="surface", help="Render mode: surface, wireframe, scatter.")
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

    if args.render_mode not in ('surface', 'wireframe', 'scatter'):
        raise TypeError("Render mode '{}' not supported".format(args.render_mode))

    plot_gamut_in_space(
        args.space,
        args.gamut,
        title=args.title,
        dark=args.dark,
        rotate_elev=args.rotate_elev,
        rotate_azim=args.rotate_azim,
        mode=args.render_mode,
        resolution=int(args.resolution),
        opacity=args.opacity
    )

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()

    plt.close()


if __name__ == "__main__":
    sys.exit(main())
