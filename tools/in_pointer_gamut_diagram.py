"""
Generate random points in and around the Pointer gamut indicate whether they are inside or outside the gamut.

If a color is given, plot it against the gamut instead of random points.
"""
import sys
import os
import random
import argparse
import plotly.graph_objects as go
import plotly.io as io

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


def plot_pointer_gamut(target, space_gamut, fit, title, height, width):
    """
    Plot the Pointer gamut and random points inside and outside the gamut.

    If a color is given, plot it against the gamut instead of random points.
    """

    default_color = 'black'

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

    suptitle = ''
    if not title:
        suptitle = f'Pointer Gamut: LCh SC at Lightness {round(lightness, 2)}'
    if target:
        if len(colors) > 1:
            space = original.space()
            title = f'Color: {colors[0].convert(space).to_string()} -> {colors[1].convert(space).to_string()}'
        else:
            title = f'Color: {colors[0].to_string()}'
        if suptitle:
            title = f"{suptitle}<br><sup>{title}</sup>"

    fig = go.Figure(
        layout={
            'title': title,
            'xaxis_title': {'text': 'hue'},
            'yaxis_title': {'text': 'chroma'},
            'polar': {'radialaxis': {'showline': False, 'layer': 'below traces'}},
            'height': height,
            'width': width
        }
    )

    fig.add_traces(data=go.Scatterpolar(
        theta=gamut.pointer.LCH_H + [0.0],
        r=chroma,
        mode="lines",
        line={'color': default_color, 'width': 2},
        showlegend=False
    ))

    inside = []
    outside = []

    for color in colors:
        c, h = color[1:-1]
        if color.in_pointer_gamut():
            inside.append([c, h])
        else:
            outside.append([c, h])

    if inside:
        y, x = zip(*inside)
        fig.add_traces(data=go.Scatterpolar(
            theta=x,
            r=y,
            mode="markers",
            marker={
                'color': default_color,
                'size': 12,
                'line': {'color': default_color, 'width': 2},
                'opacity': 1
            },
            showlegend=False
        ))

    if outside:
        y, x = zip(*outside)
        fig.add_traces(data=go.Scatterpolar(
            theta=x,
            r=y,
            mode="markers",
            marker={
                'color': default_color,
                'size': 12,
                'line': {'color': default_color, 'width': 2},
                'symbol': 'x',
                'opacity': 1
            },
            showlegend=False
        ))

    return fig


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
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--height', '-H', type=int, default=600, help="Height")
    parser.add_argument('--width', '-W', type=int, default=800, help="Width")

    args = parser.parse_args()

    fig = plot_pointer_gamut(
        args.color,
        args.gamut,
        args.fit,
        args.title,
        args.height,
        args.width
    )

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
