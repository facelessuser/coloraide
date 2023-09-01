"""Harmony diagram."""
import sys
import os
import matplotlib.pyplot as plt
import argparse
import bisect
import math

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide.util import fmt_float  # noqa: E402
from coloraide.spaces import LChish, Regular, Labish, HSLish, HSVish  # noqa: E402
from coloraide.spaces.hsl import HSL  # noqa: E402
from coloraide.spaces.lch import LCh  # noqa: E402
from coloraide import algebra as alg  # noqa: E402


class _LCh(LCh):
    """Special LCh mapping class for harmonies."""

    INDEXES = [0, 1, 2]

    def to_base(self, coords):
        """Convert to the base."""

        ordered = [0.0, 0.0, 0.0]
        for e, c in enumerate(super().to_base(coords)):
            ordered[self.INDEXES[e]] = c
        return ordered

    def from_base(self, coords):
        """Convert from the base."""

        return super().from_base([coords[i] for i in self.INDEXES])


class _HSL(HSL):
    """Special HSL mapping class for harmonies."""

    INDEXES = [0, 1, 2]

    def to_base(self, coords):
        """Convert to the base."""

        ordered = [0.0, 0.0, 0.0]
        for e, c in enumerate(super().to_base(coords)):
            ordered[self.INDEXES[e]] = c
        return ordered

    def from_base(self, coords):
        """Convert from the base."""

        return super().from_base([coords[i] for i in self.INDEXES])


def get_cylinder(color, space):
    """Create a cylinder from a select number of color spaces on the fly."""

    cs = Color.CS_MAP[space]

    if isinstance(cs, Labish):
        class CustomLCh(_LCh):
            NAME = '-custom-cylinder'
            SERIALIZE = ('---custom-cylinder',)
            BASE = cs.NAME
            WHITE = cs.WHITE
            DYAMIC_RANGE = cs.DYNAMIC_RANGE
            INDEXES = cs.indexes()

        class ColorCyl(color):
            """Custom color."""

        ColorCyl.register(CustomLCh())

        return ColorCyl

    if isinstance(cs, Regular):

        class CustomHSL(_HSL):
            NAME = '-custom-cylinder'
            SERIALIZE = ('---custom-cylinder',)
            BASE = cs.NAME
            GAMUT_CHECK = cs.NAME
            WHITE = cs.WHITE
            DYAMIC_RANGE = cs.DYNAMIC_RANGE
            INDEXES = cs.indexes() if hasattr(cs, 'indexes') else [0, 1, 2]

        class ColorCyl(color):
            """Custom color."""

        ColorCyl.register(CustomHSL())

        return ColorCyl

    raise ValueError('Unsupported color space type {}'.format(color.space()))


def plot_slice(
    create,
    space,
    constant,
    max_chroma,
    gamut='srgb',
    res=500
):
    """Plot a slice."""

    # Create a color object based on the specified space.
    custom = create(space, [])

    cs = create.CS_MAP[space]
    if isinstance(cs, (HSLish, HSVish)):
        hue, chroma, lightness = cs.names()
    else:
        lightness, chroma, hue = cs.names()

    # Interpolate between each x axis color along the y axis
    cmap = []
    x = []
    y = []
    maximums = []
    for h in alg.linspace(0, 360, res):
        custom[hue] = h
        chromas = []
        for c in alg.linspace(0, max_chroma, res):
            custom[lightness] = constant
            custom[chroma] = c
            if custom.in_gamut(gamut):
                cmap.append(custom.convert('srgb').to_string(hex=True))
                x.append(math.radians(h))
                chromas.append(c)
        mx = max(chromas)
        maximums.append((h, mx))
        y.extend(alg.divide(chromas, mx))

    # Fill colors
    plt.scatter(
        x,
        y,
        marker="o",
        color=cmap,
        s=2
    )

    return maximums


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='gamut_diagrams', description='Demonstrate gamut mapping.')
    parser.add_argument('--space', '-s', default='hsl', help="Space to interpolate in.")
    parser.add_argument('--color', '-c', help="Seed color.")
    parser.add_argument('--max-chroma', '-M', help="Maximum chroma.")
    parser.add_argument('--harmony', '-n', default='', help="Color harmony to use.")
    parser.add_argument('--gamut', '-g', default="srgb", help='Gamut to evaluate the color in (default is sRGB).')
    parser.add_argument('--map-colors', '-m', action='store_true', help="Gamut map colors to be within the gamut.")
    parser.add_argument('--gamut-map-method', '-f', help="Gamut mapping space.")
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument('--yaxis', '-y', help="The channel to plot on Y axis (other than hue or l) 'name:min:max'.")
    parser.add_argument('--resolution', '-r', default="800", help="How densely to render the figure.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')

    args = parser.parse_args()

    space = args.space
    original = space
    cs = Color.CS_MAP[space]
    if isinstance(cs, (LChish, HSLish, HSVish)):
        CustomColor = Color
    else:
        CustomColor = get_cylinder(Color, space)
        space = '-custom-cylinder'
        cs = CustomColor.CS_MAP[space]

    c_original = CustomColor(args.color)
    c1 = c_original.convert(space)

    if isinstance(cs, (HSLish, HSVish)):
        hue, chroma, lightness = cs.names()
    else:
        lightness, chroma, hue = cs.names()

    c_value = c1[lightness]

    if not args.title:
        title = "Color Harmony '{}'' in Color Space '{}' in Gamut '{}'".format(args.harmony, args.space, args.gamut)
    else:
        title = args.title

    if not args.dark:
        plt.style.use('seaborn-v0_8-darkgrid')
    else:
        plt.style.use('dark_background')

    figure = plt.figure()

    # Create axes
    ax = plt.axes(
        xlabel=hue,
        ylabel=chroma,
        projection='polar'
    )

    plt.yticks([])

    # Create titles
    if not title:
        title = "Slice of {} at {} = {}".format(original, lightness, fmt_float(c_value, 5))

    plt.title(title)

    # Set aspect
    ax.set_aspect('equal')
    figure.add_axes(ax)

    maximums = plot_slice(
        CustomColor,
        space,
        c_value,
        float(args.max_chroma),
        gamut=args.gamut,
        res=int(args.resolution)
    )

    if args.harmony:
        colors = c1.harmony(args.harmony, space=space)
        if args.map_colors:
            [c.fit(args.gamut, method=None if not args.gamut_map_method else args.gamut_map_method) for c in colors]

        hues = [m[0] for m in maximums]
        for c in colors:
            h = c[hue]
            i = bisect.bisect_left(hues, h)
            t = alg.ilerp(maximums[i][0], maximums[i + 1][0], h)
            max_c = alg.lerp(maximums[i][1], maximums[i + 1][1], t)
            norm_c = c[chroma] / max_c
            hr = math.radians(h)

            plt.scatter(
                hr,
                norm_c,
                marker="o",
                color=c.convert('srgb').to_string(hex=True),
                edgecolor='black',
                s=8 ** 2,
                zorder=100
            )
            xs = [0, hr]
            ys = [0, norm_c]

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
