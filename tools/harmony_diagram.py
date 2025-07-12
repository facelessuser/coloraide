"""Harmony diagram."""
import sys
import os
import argparse
import bisect
import plotly.graph_objects as go
import plotly.io as io
import json

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide.util import fmt_float  # noqa: E402
from coloraide.spaces import LChish, Luminant, Prism, Labish, HSLish, HSVish  # noqa: E402
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
        """Convert from RGB to HSL."""

        # Convert from HSL back to its original space
        coords = super().to_base(coords)
        # Scale and offset the values back to the origin space's configuration
        coords[0] = coords[0] * (self.SCALE_1 - self.OFFSET_1) + self.OFFSET_1
        coords[1] = coords[1] * (self.SCALE_2 - self.OFFSET_2) + self.OFFSET_2
        coords[2] = coords[2] * (self.SCALE_3 - self.OFFSET_3) + self.OFFSET_3
        ordered = [0.0, 0.0, 0.0]
        # Consistently order a given color spaces points based on its type
        for e, c in enumerate(coords):
            ordered[self.INDEXES[e]] = c
        return ordered

    def from_base(self, coords):
        """Convert from HSL to RGB."""

        # Undo order a given color spaces points based on its type
        coords = [coords[i] for i in self.INDEXES]
        # Scale and offset the values such that channels are between 0 - 1
        coords[0] = (coords[0] - self.OFFSET_1) / (self.SCALE_1 - self.OFFSET_1)
        coords[1] = (coords[1] - self.OFFSET_2) / (self.SCALE_2 - self.OFFSET_2)
        coords[2] = (coords[2] - self.OFFSET_3) / (self.SCALE_3 - self.OFFSET_3)
        # Convert to HSL
        return super().from_base(coords)


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

    if isinstance(cs, Prism) and not isinstance(cs, Luminant):

        class CustomHSL(_HSL):
            NAME = '-custom-cylinder'
            SERIALIZE = ('---custom-cylinder',)
            BASE = cs.NAME
            GAMUT_CHECK = cs.NAME
            WHITE = cs.WHITE
            DYAMIC_RANGE = cs.DYNAMIC_RANGE
            INDEXES = cs.indexes()

            # Scale channels as needed
            OFFSET_1 = cs.channels[INDEXES[0]].low
            OFFSET_2 = cs.channels[INDEXES[1]].low
            OFFSET_3 = cs.channels[INDEXES[2]].low

            SCALE_1 = cs.channels[INDEXES[0]].high
            SCALE_2 = cs.channels[INDEXES[1]].high
            SCALE_3 = cs.channels[INDEXES[2]].high

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

    if gmap is None:
        gmap = {'method': 'raytrace'}

    if 'pspace' not in gmap:
        gmap['pspace'] = cs.NAME

    # Interpolate between each x axis color along the y axis
    cmap = []
    theta = []
    r = []
    maximums = []
    for h in alg.linspace(0, 360, res):
        custom[hue] = h
        custom[lightness] = constant
        custom[chroma] = max_chroma
        custom.fit(gamut, **gmap)
        mx = custom[chroma]
        chromas = []
        for c in alg.linspace(0, mx, res):
            custom[lightness] = constant
            custom[chroma] = c
            theta.append(h)
            chromas.append(c)
            cmap.append(custom.convert('srgb').to_string(hex=True, **gmap))
        maximums.append((h, mx))
        r.extend([alg.zdiv(ci, mx) for ci in chromas])

    fig.add_traces(data=go.Scatterpolar(
        r=r,
        theta=theta,
        mode='markers',
        marker={'color': cmap, 'size': scatter_size},
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
    parser.add_argument('--pspace', '-p', help="Specific perceptual space to gamut map in.")
    parser.add_argument('--map-colors', '-m', action='store_true', help="Gamut map colors to be within the gamut.")
    parser.add_argument('--gmap', '-f', default="raytrace", help="Gamut mapping space.")
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument('--resolution', '-r', type=int, default=500, help="How densely to render the figure.")
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
        title = f"Color Harmony '{args.harmony}' in Color Space '{args.space}' in Gamut '{args.gamut}'"
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

    parts = [p.strip() if not e else json.loads(p) for e, p in enumerate(args.gmap.split(':', 1))]
    gmap = {'method': parts[0]}
    if len(parts) == 2:
        gmap.update(parts[1])

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
                f.write(fig.to_image(format=filetype, width=args.width, height=args.height))
    else:
        fig.show('browser')


if __name__ == "__main__":
    sys.exit(main())
