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
    parser.add_argument('--resolution', '-r', default="800", help="How densely to render the figure.")
    parser.add_argument('--clip-space', '-p', default='lch', help="LCh space to show clipping in.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')

    args = parser.parse_args()

    if args.method == 'lch-chroma':
        space = 'lch'
        color = Color(args.color).convert(space, in_place=True)
        color2 = color.clone().fit('srgb', method=args.method)
        mapcolor = color.convert(space)
        mapcolor2 = color2.convert(space)
        xaxis = 'c:0:160'
        yaxis = 'l:0:100'
        constant = 'h:{}'.format(fmt_float(mapcolor['hue'], 5))
        title = 'MINDE and Chroma Reduction in CIELCh'
        subtitle = '{} ==> {}'.format(color.to_string(), color2.to_string())
    elif args.method in ('oklch-chroma', 'css-color-4'):
        space = 'oklch'
        color = Color(args.color).convert(space, in_place=True)
        color2 = color.clone().fit('srgb', method=args.method)
        mapcolor = color.convert(space)
        mapcolor2 = color2.convert(space)
        xaxis = 'c:0:0.5'
        yaxis = 'l:0:1'
        constant = 'h:{}'.format(fmt_float(mapcolor['hue'], 5))
        t = 'MINDE and Chroma Reduction in OkLCh'
        if args.method == 'css-color-4':
            t += ' (CSS Color Level 4)'
        title = '{}'.format(t)
        subtitle = '{} ==> {}'.format(color.to_string(), color2.to_string())
    elif args.method == 'clip':
        space = args.clip_space
        if space not in ('lch', 'oklch'):
            raise ValueError('"{}" is an unsupported clipping space'.format(space))
        color = Color(args.color).convert(space, in_place=True)
        color2 = color.clone().fit('srgb', method=args.method)
        mapcolor = color.convert(space)
        mapcolor2 = color2.convert(space)
        xaxis = 'c:0:160' if space == 'lch' else 'c:0:0.5'
        yaxis = 'l:0:100' if space == 'lch' else 'l:0:1'
        constant = 'h:{}'.format(fmt_float(mapcolor['hue'], 5))
        t_space = 'CIELCh' if space == 'lch' else 'OkLCh'
        title = 'Clipping shown in {}'.format(t_space)
        subtitle = '{} ==> {}'.format(color.to_string(), color2.to_string())
    else:
        raise ValueError('"{}" is an unsupported gamut mapping algorithm'.format(args.method))

    plot_slice(
        space,
        constant,
        xaxis,
        yaxis,
        gamut=args.gamut,
        resolution=int(args.resolution),
        title=title,
        subtitle=subtitle,
        dark=args.dark
    )

    plt.plot(
        [mapcolor2['c'], mapcolor['c']],
        [mapcolor2['l'], mapcolor['l']],
        color='black',
        marker="",
        linewidth=1.5,
        markersize=2,
        antialiased=True
    )

    plt.scatter(
        mapcolor['c'],
        mapcolor['l'],
        marker="o",
        color=color2.convert('srgb').to_string(hex=True, fit=args.method),
        edgecolor='black',
        zorder=100
    )

    plt.scatter(
        mapcolor2['c'],
        mapcolor2['l'],
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
