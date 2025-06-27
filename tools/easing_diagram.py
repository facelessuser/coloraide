"""Plot easing functions."""
import argparse
import sys
import os
import re
import plotly.graph_objects as go
import plotly.io as io

sys.path.insert(0, os.getcwd())

from coloraide import easing  # noqa: E402

RE_BEZIER = re.compile(
    r'''(?x)
    ^(cubic_bezier)\((
        (?:\s*[+\-]?(?:[0-9]*\.)?[0-9]+(?:e[-+]?[0-9]*)?\s*,){3}
        \s*[+\-]?(?:[0-9]*\.)?[0-9]+(?:e[-+]?[0-9]*)?\s*
    )\)$
    '''
)


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='easing_diagrams', description='Plot easings.')
    parser.add_argument('--easing', '-s', default='linear', help="Space to interpolate in.")
    parser.add_argument('--extrapolate', '-e', action='store_true', help='Extrapolate values.')
    parser.add_argument('--title', '-T', default='', help="Provide a title for the diagram.")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--height', '-H', type=int, default=800, help="Height")
    parser.add_argument('--width', '-W', type=int, default=800, help="Width")
    args = parser.parse_args()

    m = RE_BEZIER.match(args.easing.strip())
    if m is not None:
        function = m.group(0).strip()
        ease = easing.cubic_bezier(*[float(v.strip()) for v in m.group(2).split(',')])
    else:
        function = args.easing.strip()
        ease = getattr(easing, function)

    xs = []
    ys = []
    if not args.extrapolate:
        offset, factor = 0, 100
    else:
        offset, factor = 25, 50
    for r in range(101):
        x = (r - offset) / factor
        xs.append(x)
        ys.append(ease(x))

    default_color = 'black'

    # Create titles
    title = args.title
    if not title:
        title = function

    fig = go.Figure(
        layout={
            'title': title,
            'xaxis_title': {'text': 'Time'},
            'yaxis_title': {'text': 'Progression'},
            'yaxis_scaleanchor': "x",
            'xaxis_scaleanchor': "y",
            'yaxis_scaleratio': 1,
            'xaxis_scaleratio': 1,
            'height': args.height,
            'width': args.width
        }
    )

    p0 = [0, 0]
    p3 = [1, 1]
    if function == 'linear':
        p1 = [0.0, 0.0]
        p2 = [1.0, 1.0]
    else:
        p1 = ease.keywords['p1']
        p2 = ease.keywords['p2']

    fig.add_traces(data=go.Scatter(
        x=xs,
        y=ys,
        mode="lines",
        line={'color': default_color, 'width': 4},
        showlegend=False
    ))

    fig.add_traces(data=go.Scatter(
        x=[p0[0], p3[0]],
        y=[p0[1], p3[1]],
        mode="markers",
        marker={'color': default_color, 'size': 12, 'symbol': 'circle'},
        showlegend=False
    ))

    fig.add_traces(data=go.Scatter(
        x=[p0[0], p1[0]],
        y=[p0[1], p1[1]],
        mode="markers+lines",
        marker={'color': 'teal', 'size': 12, 'symbol': 'circle'},
        line={'color': 'teal', 'width': 4, 'dash': 'dash'},
        showlegend=False
    ))

    fig.add_traces(data=go.Scatter(
        x=[p2[0], p3[0]],
        y=[p2[1], p3[1]],
        mode="markers+lines",
        marker={'color': 'teal', 'size': 12, 'symbol': 'circle'},
        line={'color': 'teal', 'width': 4, 'dash': 'dash'},
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
