"""
Generate random points in and around the Pointer gamut indicate whether they are inside or outside the gamut.

If a color is given, plot it against the gamut instead of random points.
"""
import sys
import os
import math
import random
import argparse
import matplotlib.pyplot as plt

sys.path.insert(0, os.getcwd())

from coloraide import gamut  # noqa: E402
from coloraide import algebra as alg  # noqa: E402
from coloraide.everything import ColorAll  # noqa: E402
from coloraide.spaces.lch import LCh  # noqa: E402
from coloraide.spaces.lab import Lab  # noqa: E402


class LabPointer(Lab):
    """Lab Pointer's Gamut."""

    BASE = 'xyz-d65'
    NAME = 'lab-pointer'
    SERIALIZE = ('--lab-pointer',)
    WHITE = gamut.pointer.WHITE_POINT_SC


class LChPointer(LCh):
    """LCh Pointer's Gamut."""

    BASE = 'lab-pointer'
    NAME = 'lch-pointer'
    SERIALIZE = ('--lch-pointer',)
    WHITE = gamut.pointer.WHITE_POINT_SC


class Color(ColorAll):
    """Custom class for Pointer conversion."""


Color.register([LabPointer(), LChPointer()])


def plot_pointer_gamut(target, space_gamut, fit, title, dark=False):
    """
    Plot the Pointer gamut and random points inside and outside the gamut.

    If a color is given, plot it against the gamut instead of random points.
    """

    if not dark:
        plt.style.use('seaborn-v0_8-darkgrid')
        default_color = 'black'
    else:
        plt.style.use('dark_background')
        default_color = 'white'

    lightness = random.uniform(15, 90)
    colors = []
    if not target:
        for _ in range(20):
            while True:
                color = Color.random('lch-pointer', limits=[(lightness, lightness), None, None])
                if color.in_gamut(space_gamut, tolerance=0):
                    colors.append(color)
                    break
    else:
        original = Color(target)
        colors.append(original.convert('lch-pointer', norm=False))
        lightness = colors[0]['l']
        if fit and not colors[0].in_pointer_gamut():
            colors.append(colors[0].clone().fit_pointer_gamut())
    color = colors[0]
    l, c, h = color[:-1]
    li, lf = gamut.pointer.closest_lightness(l)
    chroma = [alg.lerp(row[li], row[li + 1], lf) for row in gamut.pointer.LCH_POINTER]
    chroma.append(chroma[0])

    figure = plt.figure()

    ax = plt.axes(
        xlabel='hue',
        ylabel='chroma',
        projection='polar'
    )

    ax.set_aspect('equal')
    figure.add_axes(ax)

    if not title:
        plt.suptitle('Pointer Gamut: LCh SC at Lightness {}'.format(round(lightness, 2)))
    if target:
        if len(colors) > 1:
            space = original.space()
            ax.set_title(
                'Color: {} -> {}'.format(colors[0].convert(space).to_string(), colors[1].convert(space).to_string()),
                fontdict={'fontsize': 8},
                pad=2
            )
        else:
            ax.set_title('Color: {}'.format(colors[0].to_string()), fontdict={'fontsize': 8}, pad=2)

    plt.plot(
        [math.radians(hue) for hue in gamut.pointer.LCH_H] + [0.0],
        chroma,
        color=default_color,
        marker="",
        linewidth=1.5,
        markersize=2,
        antialiased=True
    )

    inside = []
    outside = []

    for color in colors:
        c, h = color[1:-1]
        if color.in_pointer_gamut():
            inside.append([c, math.radians(h)])
        else:
            outside.append([c, math.radians(h)])

    if inside:
        y, x = zip(*inside)
        plt.scatter(
            x,
            y,
            marker="o",
            color=default_color,
            edgecolor=default_color,
            s=16,
            zorder=100
        )

    if outside:
        y, x = zip(*outside)
        plt.scatter(
            x,
            y,
            marker="x",
            color=default_color,
            s=16,
            zorder=100
        )


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='pointer_gamut_diagram', description='Plot random points in relation to Pointer gamut.'
    )
    parser.add_argument(
        '--gamut', '-g', default="display-p3", help='Gamut to evaluate the color in (default is display-p3).'
    )
    parser.add_argument('--fit', '-f', action="store_true", help="Fit color to pointer gamut.")
    parser.add_argument(
        '--color', '-c',
        help="Color to test against the Pointer gamut, single colors will show the original and fitted color."
    )
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')

    args = parser.parse_args()

    plot_pointer_gamut(
        args.color,
        args.gamut,
        args.fit,
        args.title,
        dark=args.dark
    )

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
