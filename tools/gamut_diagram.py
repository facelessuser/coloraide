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
    parser.add_argument('--resolution', '-r', default="800", help="How densely to render the figure.")
    parser.add_argument('--clip-space', '-p', default='lch', help="LCh space to show clipping in.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument(
        '--jnd', type=float, default=-1.0,
        help="Set the JND for MINDE approaches. If set to -1, default JND is used."
    )
    parser.add_argument('--pspace', default='oklch', help="Set the perceptual space for raytrace method.")
    args = parser.parse_args()
    method = args.method

    pspace = ''
    if method == 'clip':
        if args.clip_space not in ('lch', 'oklch', 'hct'):
            raise ValueError(f'"{args.clip_space}" is an unsupported clipping space')
        pspace = args.clip_space
    elif method == 'raytrace':
        pspace = args.pspace
    elif method.endswith('-chroma'):
        pspace = '-'.join(method.split('-')[:-1])

    if (method.endswith('-chroma') and pspace == 'lch') or pspace == 'lch-d65':
        space = 'lch-d65'
        t_space = 'CIELCh D65'
        xaxis = 'c:0:264'
        yaxis = 'l:0:100'
        x = 'c'
        y = 'l'
    elif pspace == 'oklch':
        space = 'oklch'
        t_space = 'OkLCh'
        xaxis = 'c:0:1.5'
        yaxis = 'l:0:1'
        x = 'c'
        y = 'l'
    elif pspace == 'hct':
        space = 'hct'
        t_space = 'HCT'
        xaxis = 'c:0:267'
        yaxis = 't:0:100'
        x = 'c'
        y = 't'
    else:
        raise ValueError(f'"{args.method}" is an unsupported gamut mapping algorithm')

    if args.method == 'clip':
        title = f'Clipping shown in {t_space}'
    elif args.method.endswith('-chroma'):
        title = f'MINDE and Chroma Reduction in {t_space}'
    elif args.method.endswith('raytrace') or args.method.startswith('raytrace'):
        title = f'Ray Tracing Chroma Reduction in {t_space}'

    jnd = None if args.jnd == -1 else args.jnd
    gmap = {'method': args.method, 'jnd': jnd, 'pspace': pspace}

    orig = Color(args.color)
    color = orig.convert(space, in_place=True)
    color2 = color.clone().fit(args.gamut, **gmap)
    mapcolor = color.convert(space)
    mapcolor2 = color2.convert(space)
    constant = 'h:{}'.format(fmt_float(mapcolor['hue'], 5))
    subtitle = f'{color.to_string()} ==> {color2.to_string()}'

    plot_slice(
        space,
        constant,
        xaxis,
        yaxis,
        gamut=args.gamut,
        gmap=gmap,
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
        color=color2.convert('srgb').to_string(hex=True, fit=gmap),
        edgecolor='black',
        zorder=100
    )

    plt.scatter(
        mapcolor2[x],
        mapcolor2[y],
        marker="o",
        color=color2.convert('srgb').to_string(hex=True, fit=gmap),
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
