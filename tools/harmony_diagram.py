"""Harmony diagram."""
import sys
import os
import argparse
import bisect
import plotly.graph_objects as go
import plotly.io as io

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

    raise ValueError(f'Unsupported color space type {color.space()}')


def plot_slice(
    fig,
    create,
    space,
    constant,
    max_chroma,
    gamut='srgb',
    gmap=None,
    res=500,
    scatter_size=16
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
    theta = []
    r = []
    maximums = []
    for h in alg.linspace(0, 360, res):
        custom[hue] = h
        custom[lightness] = constant
        custom[chroma] = max_chroma
        custom.fit(gamut, method=gmap)
        mx = custom[chroma]
        chromas = []
        for c in alg.linspace(0, mx, res):
            custom[lightness] = constant
            custom[chroma] = c
            theta.append(h)
            chromas.append(c)
            cmap.append(custom.convert('srgb').to_string(hex=True, fit=gmap))
        maximums.append((h, mx))
        r.extend(alg.divide(chromas, mx))

    fig.add_traces(data=go.Scatterpolar(
        r=r,
        theta=theta,
        mode='markers',
        marker={'color': cmap, 'size': 16},
        showlegend=False
    ))

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
    parser.add_argument('--gamut-map-method', '-f', default="raytrace", help="Gamut mapping space.")
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument('--resolution', '-r', type=int, default=400, help="How densely to render the figure.")
    parser.add_argument('--scatter-size', '-S', type=int, default=4, help="Define scatter plot size.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--height', '-H', type=int, default=800, help="Height")
    parser.add_argument('--width', '-W', type=int, default=800, help="Width")


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
        title = f"Color Harmony '{args.harmony}'' in Color Space '{args.space}' in Gamut '{args.gamut}'"
    else:
        title = args.title

    # Create titles
    if not title:
        title = f"Slice of {original} at {lightness} = {fmt_float(c_value, 5)}"

    fig = go.Figure(
        layout={
            'title': title,
            'polar': {'radialaxis': {'showline': False, 'tickvals': []}},
            'height': args.height,
            'width': args.width
        }
    )

    gmap = args.gamut_map_method

    maximums = plot_slice(
        fig,
        CustomColor,
        space,
        c_value,
        float(args.max_chroma),
        gamut=args.gamut,
        gmap=gmap,
        res=args.resolution,
        scatter_size=int(args.scatter_size)
    )

    if args.harmony:
        colors = c1.harmony(args.harmony, space=space)

        if args.map_colors:
            [c.fit(args.gamut, method=gmap) for c in colors]

        hues1 = [c[hue] % 360 for c in colors]
        chromas = [c[chroma] for c in colors]
        hues2 = [m[0] for m in maximums]

        for e, h in enumerate(hues1):
            # Find the points in our hue/chroma map
            i = bisect.bisect_left(hues2, h)
            if i == 0:
                start = len(hues2) - 1
                end = 0
            elif i == len(hues2):
                end = 0
                start = i - 1
            else:
                start = i - 1
                end = i

            # Ensure we account for wrapping from 360 to 0
            h1 = maximums[start][0]
            h2 = maximums[end][1]
            dh = (h1 - h2)
            if dh > 180:
                h2 += 360

            # Use inverse interpolation to determine where between our hue map we are.
            # Then use that point to calculate the approximate max chroma for that hue.
            # Use that to normalize the chroma of the points on the plot.
            t = alg.ilerp(h1, h2, h)
            max_c = alg.lerp(maximums[start][1], maximums[end][1], t)
            norm_c = chromas[e] / max_c

            fig.add_traces(data=go.Scatterpolar(
                r=[0, norm_c],
                theta=[0, h],
                mode="lines+markers",
                line={'color': 'black', 'width': 2},
                marker={
                    'color': colors[e].convert('srgb').to_string(hex=True, fit=gmap),
                    'size': [0, 16],
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
                f.write(fig.to_image(format=filetype))
    else:
        fig.show()


if __name__ == "__main__":
    sys.exit(main())
