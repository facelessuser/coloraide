"""Model gamut mapping."""
import sys
import os
import matplotlib.pyplot as plt
import argparse

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from tools.slice_diagram import plot_slice  # noqa: E402
from coloraide.util import fmt_float  # noqa: E402


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='gamut_diagrams', description='Demonstrate gamut mapping.')
    parser.add_argument('--color', '-c', help="Color to gamut map.")
    parser.add_argument('--method', '-m', default='lch-chroma', help="Gamut map method")
    parser.add_argument('--gamut', '-g', default="srgb", help='Gamut to evaluate the color in (default is sRGB).')
    parser.add_argument('--no-border', '-b', action="store_true", help='Draw no border around the graphed content.')
    parser.add_argument('--resolution', '-r', default="500", help="How densely to render the figure.")
    parser.add_argument('--clip-space', '-p', default='lch', help="LCh space to show clipping in.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')

    args = parser.parse_args()
    method = args.method

    if method == 'clip':
        if args.clip_space not in ('lch', 'oklch', 'hct'):
            raise ValueError('"{}" is an unsupported clipping space'.format(args.clip_space))
        method = args.clip_space + '-chroma'

    if method == 'lch-chroma':
        space = 'lch'
        t_space = 'CIELCh'
        xaxis = 'c:0:264'
        yaxis = 'l:0:100'
        x = 'c'
        y = 'l'
    elif method == 'oklch-chroma':
        space = 'oklch'
        t_space = 'OkLCh'
        xaxis = 'c:0:1.5'
        yaxis = 'l:0:1'
        x = 'c'
        y = 'l'
    elif method == 'hct-chroma':
        space = 'hct'
        t_space = 'HCT'
        xaxis = 'c:0:267'
        yaxis = 't:0:100'
        x = 'c'
        y = 't'
    else:
        raise ValueError('"{}" is an unsupported gamut mapping algorithm'.format(args.method))

    if args.method == 'clip':
        title = 'Clipping shown in {}'.format(t_space)
    else:
        title = 'MINDE and Chroma Reduction in {}'.format(t_space)

    color = Color(args.color).convert(space, in_place=True)
    color2 = color.clone().fit('srgb', method=args.method)
    mapcolor = color.convert(space)
    mapcolor2 = color2.convert(space)
    constant = 'h:{}'.format(fmt_float(mapcolor['hue'], 5))
    subtitle = '{} ==> {}'.format(color.to_string(), color2.to_string())

    plot_slice(
        space,
        constant,
        xaxis,
        yaxis,
        gamut=args.gamut,
        resolution=int(args.resolution),
        title=title,
        subtitle=subtitle,
        dark=args.dark,
        border=not args.no_border
    )

    plt.plot(
        [mapcolor2[x], mapcolor[x]],
        [mapcolor2[y], mapcolor[y]],
        color='black',
        marker="",
        linewidth=1.5,
        markersize=2,
        antialiased=True
    )

    plt.scatter(
        mapcolor[x],
        mapcolor[y],
        marker="o",
        color=color2.convert('srgb').to_string(hex=True, fit=args.method),
        edgecolor='black',
        zorder=100
    )

    plt.scatter(
        mapcolor2[x],
        mapcolor2[y],
        marker="o",
        color=color2.convert('srgb').to_string(hex=True, fit=args.method),
        edgecolor='black',
        zorder=100
    )

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
