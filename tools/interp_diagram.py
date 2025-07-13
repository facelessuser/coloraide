"""
Model interpolation.

Currently only shows non polar interpolation.
"""
import sys
import os
import plotly.graph_objects as go
import plotly.io as io
import argparse
import json

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from tools.slice_diagram import plot_slice  # noqa: E402
from coloraide import algebra as alg  # noqa: E402


def get_spline(x, y, steps=100):
    """Get spline."""

    return tuple([*i] for i in zip(*alg.interpolate([*zip(x, y)], method='monotone').steps(steps)))


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='gamut_diagrams', description='Demonstrate gamut mapping.')
    parser.add_argument('--space', '-s', default='srgb', help="Space to interpolate in.")
    parser.add_argument('--color', '-c', action='append', help="Color.")
    parser.add_argument('--position', '-p', type=float, help="Position between to show interpolated.")
    parser.add_argument('--gamut', '-g', default="srgb", help='Gamut to evaluate the color in (default is sRGB).')
    parser.add_argument('--method', '-m', default='linear', help="Interplation method to use: linear, bezier, etc.")
    parser.add_argument('--extrapolate', '-e', action='store_true', help='Extrapolate values.')
    parser.add_argument('--powerless', '-P', action='store_true', help="Treat achromatic hues as powerless.")
    parser.add_argument('--carryforward', '-f', action='store_true', help="Carry forward undefined channels.")
    parser.add_argument('--hue', '-u', default='shorter', help="Hue interpolation method.")
    parser.add_argument('--title', '-T', default='', help="Provide a title for the diagram.")
    parser.add_argument('--subtitle', '-t', default='', help="Provide a subtitle for the diagram.")
    parser.add_argument(
        '--constant',
        '-k',
        help=(
            "The channel to hold constant and the value to use 'name:value'. This will overwrite whatever the start"
            " and end color specifies as the plot must fit in the 2D plane."
        )
    )
    parser.add_argument(
        '--gmap',
        default='lch-chroma:{}',
        help='Options to pass to the gamut mapping method (JSON string).'
    )
    parser.add_argument('--xaxis', '-x', help="The channel to plot on X axis 'name:min:max'.")
    parser.add_argument('--yaxis', '-y', help="The channel to plot on Y axis 'name:min:max'.")
    parser.add_argument('--resolution', '-r', default="800", help="How densely to render the figure.")
    parser.add_argument('--no-border', '-b', action="store_true", help='Draw no border around the graphed content.')
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--height', '-H', type=int, default=600, help="Height")
    parser.add_argument('--width', '-W', type=int, default=800, help="Width")

    args = parser.parse_args()

    parts = [p.strip() if not e else json.loads(p) for e, p in enumerate(args.gmap.split(':', 1))]
    gmap = {'method': parts[0]}
    if len(parts) == 2:
        gmap.update(parts[1])

    colors = []
    for color in args.color:
        c = Color(color).convert(args.space)
        colors.append(c)

    for chan in args.constant.split(';'):
        c_name, c_value = chan.split(':')
        c_value = float(c_value)
        for color in colors:
            color.set(c_name, c_value)

    if not args.title:
        title = f"Interpolation in the {args.space} Color Space Using the {args.gamut} Gamut"
    else:
        title = args.title

    fig = plot_slice(
        args.space,
        args.constant,
        args.xaxis,
        args.yaxis,
        gamut=args.gamut,
        resolution=int(args.resolution),
        title=title,
        subtitle=args.subtitle,
        polar=True,
        border=not args.no_border,
        height=args.height,
        width=args.width,
        gmap=gmap
    )

    # Get the actual indexes of the specified channels
    c1 = colors[0]
    name1 = args.xaxis.split(":", 1)[0]
    name2 = args.yaxis.split(":", 1)[0]
    name1 = c1._space.CHANNEL_ALIASES.get(name1, name1)
    index1 = c1._space.get_channel_index(name1)
    name2 = c1._space.CHANNEL_ALIASES.get(name2, name2)

    is_polar = False
    if c1._space.is_polar():
        index = c1._space.hue_index()
        if index == index1:
            is_polar = True

    xs = []
    ys = []
    i = Color.interpolate(
        colors,
        space=args.space,
        method=args.method,
        extrapolate=args.extrapolate,
        powerless=args.powerless,
        carryforward=args.carryforward,
        hue=args.hue
    )
    if not args.extrapolate:
        offset, factor = 0, 1
    else:
        offset, factor = 1, 3
    for r in range(101):
        c = i((r * factor / 100) - offset)
        xs.append(c.get(name1))
        ys.append(c.get(name2))

    xs, ys = get_spline(xs, ys, len(xs) * 3)

    if is_polar:
        fig.add_traces(data=go.Scatterpolar(
            theta=xs,
            r=ys,
            mode="lines",
            line={'color': '#000000', 'width': 2},
            showlegend=False
        ))
    else:
        fig.add_traces(data=go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            line={'color': '#000000', 'width': 2},
            showlegend=False
        ))

    for c in colors:
        if is_polar:
            fig.add_traces(data=go.Scatterpolar(
                theta=[c.get(name1, nans=False)],
                r=[c.get(name2)],
                mode="markers",
                marker={
                    'color': c.convert('srgb').to_string(hex=True),
                    'size': 12,
                    'line': {'color': 'black', 'width': 2},
                    'opacity': 1
                },
                showlegend=False
            ))
        else:
            fig.add_traces(data=go.Scatter(
                x=[c.get(name1)],
                y=[c.get(name2)],
                mode="markers",
                marker={
                    'color': c.convert('srgb').to_string(hex=True),
                    'size': 12,
                    'line': {'color': 'black', 'width': 2},
                    'opacity': 1
                },
                showlegend=False
            ))

    if args.position is not None:
        cp = Color.interpolate(
            colors,
            space=args.space,
            method=args.method,
            extrapolate=args.extrapolate,
            powerless=args.powerless,
            carryforward=args.carryforward,
            hue=args.hue
        )(float(args.position))
        if is_polar:
            fig.add_traces(data=go.Scatterpolar(
                theta=[cp.get(name1, nans=False)],
                r=[cp.get(name2)],
                mode="markers",
                marker={
                    'color': cp.convert('srgb').to_string(hex=True),
                    'size': 12,
                    'line': {'width': 2},
                    'opacity': 1.5
                },
                showlegend=False
            ))
        else:
            fig.add_traces(data=go.Scatter(
                x=[cp.get(name1)],
                y=[cp.get(name2)],
                mode="markers",
                marker={
                    'color': cp.convert('srgb').to_string(hex=True),
                    'size': 14,
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
