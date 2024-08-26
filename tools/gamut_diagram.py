"""Model gamut mapping."""
import sys
import os
import matplotlib.pyplot as plt
import argparse
import math
import json

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from tools.slice_diagram import plot_slice  # noqa: E402
from coloraide.util import fmt_float  # noqa: E402
from coloraide import algebra as alg  # noqa: E402


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='gamut_diagrams', description='Demonstrate gamut mapping.')
    parser.add_argument(
        '--color', '-c',
        help="Colors to gamut map separated with semicolons. If multiple colors are used, colors must use the same hue."
    )
    parser.add_argument('--method', '-m', default='lch-chroma', help="Gamut map method")
    parser.add_argument(
        '--gmap-options',
        default='{}',
        help='Options to pass to the gamut mapping method (JSON string).'
    )
    parser.add_argument('--gamut', '-g', default="srgb", help='Gamut to evaluate the color in (default is sRGB).')
    parser.add_argument('--no-border', '-b', action="store_true", help='Draw no border around the graphed content.')
    parser.add_argument('--resolution', '-r', default="800", help="How densely to render the figure.")
    parser.add_argument('--clip-space', '-p', default='lch', help="LCh space to show clipping in.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--title', '-t', default='', help='Title.')
    parser.add_argument(
        '--show-end-pt', '-s', action='store_true', help="Show the end point of gamut mapping with color preview."
    )
    args = parser.parse_args()

    method = args.method
    gmap = {'method': args.method}
    gmap.update(json.loads(args.gmap_options))
    adaptive = gmap.get('adaptive', None)

    pspace = ''
    if method == 'clip':
        if args.clip_space not in ('lch', 'oklch', 'hct'):
            raise ValueError(f'"{args.clip_space}" is an unsupported clipping space')
        pspace = args.clip_space
    elif method == 'raytrace':
        pspace = gmap.get('pspace', 'oklch')
    elif method.endswith('-chroma') and not method.startswith('minde'):
        pspace = '-'.join(method.split('-')[:-1])
    elif method == 'minde-chroma':
        pspace = gmap.get('pspace', 'oklch')

    if (method.endswith('-chroma') and not method.startswith('minde') and pspace == 'lch') or pspace == 'lch-d65':
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

    title = ''
    if args.title:
        title = args.title
    elif args.method == 'clip':
        title = f'Clipping shown in {t_space}'
    elif args.method.endswith('-chroma'):
        title = f'MINDE and Chroma Reduction in {t_space}'
    elif args.method.endswith('raytrace') or args.method.startswith('raytrace'):
        title = f'Ray Tracing Chroma Reduction in {t_space}'

    colors = args.color.split(';')
    count = len(colors)
    start = []
    end = []
    subtitle = ''
    hue = 0

    for e, color in enumerate(colors):
        orig = Color(color)
        color = orig.convert(space, in_place=True)
        color2 = color.clone().fit(args.gamut, **gmap)
        mapcolor = color.convert(space)
        mapcolor2 = color2.convert(space)
        if e == 0:
            hue = mapcolor['hue']
            constant = 'h:{}'.format(fmt_float(hue, 5))
        else:
            hue2 = mapcolor['hue']
            if hue != hue2 and not math.isnan(hue2):
                raise ValueError("When specifying multiple colors, they are required to have the same hue.")
        if e == 0:
            if count == 1:
                subtitle = f'{color.to_string()} ==> {color2.to_string()}'
            else:
                subtitle = f'{constant}'
        start.append(mapcolor)
        end.append(mapcolor2)

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

    for i in range(count):
        mapcolor = start[i]
        mapcolor2 = end[i]
        plt.plot(
            [mapcolor2[x], mapcolor[x]],
            [mapcolor2[y], mapcolor[y]],
            color='#aaaaaa',
            marker="",
            linewidth=1.5,
            markersize=2,
            antialiased=True
        )

        if adaptive is not None:
            plt.plot(
                [mapcolor2[x], 0],
                [mapcolor2[y], alg.lerp(mapcolor2[y], mapcolor[y], alg.ilerp(mapcolor2[x], mapcolor[x], 0))],
                color='#aaaaaa88',
                marker="",
                linewidth=1.5,
                markersize=2,
                antialiased=True
            )

        plt.scatter(
            mapcolor[x],
            mapcolor[y],
            marker="o",
            color=mapcolor2.convert('srgb').to_string(hex=True, fit=gmap),
            edgecolor='black',
            zorder=100
        )

        if args.show_end_pt:
            plt.scatter(
                mapcolor2[x],
                mapcolor2[y],
                marker="o",
                color=mapcolor2.convert('srgb').to_string(hex=True, fit=gmap),
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
