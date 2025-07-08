"""Model gamut mapping."""
import sys
import os
import plotly.graph_objects as go
import plotly.io as io
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
    parser.add_argument(
        '--gmap',
        default='lch-chroma:{}',
        help='Options to pass to the gamut mapping method (JSON string).'
    )
    parser.add_argument('--gamut', '-g', default="srgb", help='Gamut to evaluate the color in (default is sRGB).')
    parser.add_argument('--no-border', '-b', action="store_true", help='Draw no border around the graphed content.')
    parser.add_argument('--resolution', '-r', default="800", help="How densely to render the figure.")
    parser.add_argument('--clip-space', '-p', default='lch', help="LCh space to show clipping in.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--title', '-t', default='', help='Title.')
    parser.add_argument(
        '--show-end-pt', '-s', action='store_true', help="Show the end point of gamut mapping with color preview."
    )
    parser.add_argument('--height', '-H', type=int, default=600, help="Height")
    parser.add_argument('--width', '-W', type=int, default=800, help="Width")
    args = parser.parse_args()

    parts = [p.strip() if not e else json.loads(p) for e, p in enumerate(args.gmap.split(':', 1))]
    method = parts[0]
    gmap = {'method': method}
    if len(parts) == 2:
        gmap.update(parts[1])
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
        raise ValueError(f"\"{gmap['method']}\" is an unsupported gamut mapping algorithm")

    title = ''
    if args.title:
        title = args.title
    elif gmap['method'] == 'clip':
        title = f'Clipping shown in {t_space}'
    elif gmap['method'].endswith('-chroma'):
        title = f'MINDE and Chroma Reduction in {t_space}'
    elif gmap['method'].endswith('raytrace') or args.method.startswith('raytrace'):
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

    fig = plot_slice(
        space,
        constant,
        xaxis,
        yaxis,
        gamut=args.gamut,
        gmap=gmap,
        resolution=int(args.resolution),
        title=title,
        subtitle=subtitle,
        border=not args.no_border,
        height=args.height,
        width=args.width
    )

    for i in range(count):
        mapcolor = start[i]
        mapcolor2 = end[i]

        fig.add_traces(data=go.Scatter(
            x=[mapcolor2[x], mapcolor[x]],
            y=[mapcolor2[y], mapcolor[y]],
            mode="lines",
            line={'color': '#aaaaaa', 'width': 2},
            showlegend=False
        ))

        if adaptive is not None:
            fig.add_traces(data=go.Scatter(
                x=[mapcolor2[x], 0],
                y=[mapcolor2[y], alg.lerp(mapcolor2[y], mapcolor[y], alg.ilerp(mapcolor2[x], mapcolor[x], 0))],
                mode="lines",
                line={'color': '#aaaaaa', 'width': 2},
                showlegend=False,
                opacity=0.5
            ))

        fig.add_traces(data=go.Scatter(
            x=[mapcolor[x]],
            y=[mapcolor[y]],
            mode="markers",
            marker={
                'color': mapcolor2.convert('srgb').to_string(hex=True, fit=gmap),
                'size': 12,
                'line': {'width': 2},
                'opacity': 1
            },
            showlegend=False
        ))

        if args.show_end_pt:
            fig.add_traces(data=go.Scatter(
                x=[mapcolor2[x]],
                y=[mapcolor2[y]],
                mode="markers",
                marker={
                    'color': mapcolor2.convert('srgb').to_string(hex=True, fit=gmap),
                    'size': 12,
                    'line': {'width': 2},
                    'opacity': 1
                },
                showlegend=False
            ))

    if args.output:
        filetype = os.path.splitext(args.output)[1].lstrip('.').lower()
        if filetype == 'html':
            with open(args.output, 'w') as f:
                f.write(io.to_html(fig))
        elif filetype == 'json':
            io.write_json(fig, args.output)
        else:
            with open(args.output, 'wb') as f:
                f.write(fig.to_image(format=filetype, width=args.width, height=args.height))
    else:
        fig.show('browser')


if __name__ == "__main__":
    sys.exit(main())
