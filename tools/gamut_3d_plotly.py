"""Plot color space using Plotly."""
import sys
import argparse
from coloraide.everything import ColorAll as Color
from scipy.spatial import Delaunay
from coloraide import algebra as alg
from plotly.figure_factory._trisurf import trisurf
import math
from coloraide.spaces import HSLish, HSVish, Cylindrical, Labish, LChish
import plotly.graph_objects as go
import plotly.io as io


def create_custom_hsl(gamut):
    """Create a custom color object that has access to a special `hsl-gamut` space to map surface in."""

    cs = Color.CS_MAP[gamut]

    class HSL(type(Color.CS_MAP['hsl'])):
        NAME = 'hsl-{}'.format(gamut)
        BASE = gamut
        GAMUT_CHECK = gamut
        WHITE = cs.WHITE
        DYAMIC_RANGE = cs.DYNAMIC_RANGE

    class ColorCyl(Color):
        """Custom color."""

    ColorCyl.register(HSL())

    return ColorCyl


def cyl_disc(ColorCyl, space, location, resolution, opacity, edges):
    """
    Plot cylindrical disc on either top or bottom of an RGB cylinder.

    Excpectation is either a HSL, HSV, or HSB style cylinder.
    """

    x = []
    y = []
    z = []
    cmap = []
    cs = ColorCyl.CS_MAP[space]
    factor = cs.channels[1].high
    if isinstance(cs, (HSVish, HSLish)):
        space_type = 'hslish/hsvish'
    else:
        space_type = space

    b = 0.0 if location == 'bottom' else 1.0 * factor
    start, end = (1.0 * factor, 0.0) if location == 'bottom' else (0.0, 1.0 * factor)

    # Interpolate a circle on the outer edge
    c1 = ColorCyl(space, [0, start, b], opacity)
    c2 = ColorCyl(space, [359.99999, start, b], opacity)
    s1 = ColorCyl.steps([c1, c2], steps=resolution, space=space, hue='specified')
    chan_name = str(c1._space.channels[1])
    s2 = [c.clone().set(chan_name, end) for c in s1]

    # Interpolate concentrical circle to the center of the disc
    step = int(resolution / 4)
    for r in range(step + 1):
        if location == 'bottom':
            r = step - r

        for t1, t2 in zip(s1, s2):
            c = t1.mix(t2, r / step, space=space, hue='specified')

            # HSL and HSV spaces
            if space_type == 'hslish/hsvish':
                hue, saturation, lightness = c._space.indexes()
                x.append(c[saturation] * math.cos(math.radians(c[hue])))
                y.append(c[saturation] * math.sin(math.radians(c[hue])))
                z.append(c[lightness])

            # HWB
            else:
                hue = c._space.hue_index()
                a, b = 1, 2
                x.append(c[a] * math.cos(math.radians(c[hue])))
                y.append(c[a] * math.sin(math.radians(c[hue])))
                z.append(c[b])

            # Ensure colors fit in output color gamut.
            s = c.convert('srgb')
            if not s.in_gamut():
                s.fit()
            else:
                s.clip()
            cmap.append(s.to_string(hex=True))

    # Calcualte triangles
    tri = Delaunay(list(zip(x, y)))

    # Generate triangulated surface
    trace = trisurf(
        x=x, y=y, z=z,
        simplices=tri.simplices,
        show_colorbar=False,
        edges_color="rgb(50, 50, 50)",
        scale=None,
        plot_edges=edges,
        color_func=[cmap[t[1]] for t in tri.simplices]
    )
    trace[0].update(opacity=opacity)
    return trace


def render_space_cyl(fig, space, gamut, resolution, opacity, edges):
    """
    Renders the color space using an RGB cylinder that is then mapped to the given space.

    Ideally used to represent cylindrical spaces and will align the the lightness equivalent
    as the Z axis. Lab-ish colors are performed in the mode as they are essentially cylindrical
    with the chroma and hue converted to Cartesian a and b.
    """

    u = []
    v = []
    x = []
    y = []
    z = []
    cmap = []

    target = Color.CS_MAP[space]
    is_cyl = isinstance(target, Cylindrical)
    is_labish = isinstance(target, Labish)
    is_lchish = isinstance(target, LChish)
    is_hslish = isinstance(target, HSLish)
    is_hslish_hsvish = is_hslish or isinstance(target, HSVish)

    # Determine the gamut mapping space to use.
    # Some spaces cannot be generalized (HWB and HPLuv for instance).
    if space in ('hwb', 'hpluv'):
        ColorCyl = Color
        gamut_space = space
    else:
        ColorCyl = create_custom_hsl(gamut)
        gamut_space = 'hsl-{}'.format(gamut)
    gspace = ColorCyl.CS_MAP[gamut_space]

    # Adjust scaling factor if the mapping space requires it
    factor = gspace.channels[1].high

    # Interpolate the sides of the cylincer at 0 and 180 degrees
    c1 = ColorCyl(gamut_space, [0, 1 * factor, 1 * factor], opacity)
    c2 = ColorCyl(gamut_space, [0, 1 * factor, 0], opacity)
    c3 = ColorCyl(gamut_space, [359.99999, 1 * factor, 1 * factor], opacity)
    c4 = ColorCyl(gamut_space, [359.99999, 1 * factor, 0], opacity)
    s1 = ColorCyl.steps([c1, c2], steps=resolution, space=gamut_space)
    s2 = ColorCyl.steps([c3, c4], steps=resolution, space=gamut_space)

    # Create a 3D mesh by interpolating the the degree ring at each point down the cylinder side.
    for t1, t2 in zip(s1, s2):
        for c in ColorCyl.steps([t1, t2], steps=resolution, space=gamut_space, hue='specified'):
            u.append(c[2])
            v.append(c['hue'])
            c.convert(space, norm=False, in_place=True)
            # LCh spaces
            if is_lchish:
                light, chroma, hue = c._space.names()
                a, b = alg.polar_to_rect(c[chroma], c[hue])
                x.append(a)
                y.append(b)
                z.append(c[light])

            # HSL and HSV spaces
            elif is_hslish_hsvish:
                hue, sat, light = c._space.names()
                a, b = alg.polar_to_rect(c[sat], c[hue])
                x.append(a)
                y.append(b)
                z.append(c[light])

            # HWB or any other cylindrical space that doesn't fit in the categories above.
            elif is_cyl:
                hue = c._space.hue_index()
                a, b = alg.polar_to_rect(c[1], c[hue])
                x.append(a)
                y.append(b)
                z.append(c[2])

            # Lab spaces
            elif is_labish:
                light, a, b = c._space.names()
                x.append(c[a])
                y.append(c[b])
                z.append(c[light])

            # Non-cylindrical spaces could be done here, but normally are not.
            else:
                x.append(c[0])
                y.append(c[1])
                z.append(c[2])

            # Adjust gamut to precicely fit
            s = c.convert('srgb')
            if not s.in_gamut():
                s.fit()
            else:
                s.clip()

            cmap.append(s.to_string(hex=True))

    # Calculate the triangles
    tri = Delaunay(list(zip(u, v)))

    # Build the triangulated surface
    trace = trisurf(
        x=x, y=y, z=z,
        simplices=tri.simplices,
        show_colorbar=False,
        edges_color="rgb(50, 50, 50)",
        scale=None,
        plot_edges=edges,
        color_func=[cmap[t[1]] for t in tri.simplices]
    )
    trace[0].update(opacity=opacity)
    fig.add_traces(trace)

    # In cases of RGB cylinders, it makes sense to generate the tops and bottoms if they are missing.
    # Since these are unique to the space, we normally generate them in the space itself instead of some
    # mapping space. These are only needed with HSL and HWB spaces.
    if is_hslish or space == 'hwb':
        target = gspace.channels[1].high
        # Tops are not usually present in either HSL or HWB without explicitely generating them.
        fig.add_traces(cyl_disc(ColorCyl, space, 'top', resolution, opacity, edges))
        # We normally get a bottom except in the case of HWB.
        if space == 'hwb':
            fig.add_traces(cyl_disc(ColorCyl, space, 'bottom', resolution, opacity, edges))

    return fig

def render_rect_face(s1, s2, dim, space, gamut, resolution, opacity, edges):
    """Render the RGB rectangular face."""

    x = []
    y = []
    z = []
    a = []
    b = []
    c = []
    cmap = []

    # Render an RGB face by taking to interpolated sides and interplating the points across the face
    for c1, c2 in zip(s1, s2):
        for t in Color.steps([c1, c2], steps=int(resolution / 4), space=gamut):
            x.append(t[0])
            y.append(t[1])
            z.append(t[2])
            t.convert(space, norm=False, in_place=True)
            a.append(t[0])
            b.append(t[1])
            c.append(t[2])

            # Fit colors to output gamut
            s = t.convert('srgb')
            if not s.in_gamut():
                s.fit()
            else:
                s.clip()
            cmap.append(s.to_string(hex=True))

    # Calculate triangles
    tri = Delaunay(list(zip(locals().get(dim[0]), locals().get(dim[1]))))

    # Generate triangulated surface
    trace = trisurf(
        x=a, y=b, z=c,
        simplices=tri.simplices,
        show_colorbar=False,
        edges_color="rgb(50, 50, 50)",
        scale=None,
        plot_edges=edges,
        color_func=[cmap[t[1]] for t in tri.simplices]
    )
    trace[0].update(opacity=opacity)
    return trace


def render_space_rect(fig, space, gamut, resolution, opacity, edges):
    """Render rectangular space."""

    # Six corners of the RGB cube
    ck = Color(gamut, [0, 0, 0], opacity)
    cw = Color(gamut, [1, 1, 1], opacity)
    cr = Color(gamut, [1, 0, 0], opacity)
    cg = Color(gamut, [0, 1, 0], opacity)
    cb = Color(gamut, [0, 0, 1], opacity)
    cy = Color(gamut, [1, 1, 0], opacity)
    cc = Color(gamut, [0, 1, 1], opacity)
    cm = Color(gamut, [1, 0, 1], opacity)

    # Interpolate two sides of a given face and interpolate the rest
    s1 = Color.steps([cy, cw], steps=resolution, space=gamut)
    s2 = Color.steps([cg, cc], steps=resolution, space=gamut)
    s3 = Color.steps([cr, cm], steps=resolution, space=gamut)
    s4 = Color.steps([ck, cb], steps=resolution, space=gamut)
    fig.add_traces(render_rect_face(s1, s2, ('x', 'z'), space, gamut, resolution, opacity, edges))
    fig.add_traces(render_rect_face(s1, s3, ('y', 'z'), space, gamut, resolution, opacity, edges))
    fig.add_traces(render_rect_face(s3, s4, ('x', 'z'), space, gamut, resolution, opacity, edges))
    fig.add_traces(render_rect_face(s4, s2, ('y', 'z'), space, gamut, resolution, opacity, edges))
    s1 = Color.steps([cb, cc], steps=resolution, space=gamut)
    s2 = Color.steps([cm, cw], steps=resolution, space=gamut)
    fig.add_traces(render_rect_face(s1, s2, ('x', 'y'), space, gamut, resolution, opacity, edges))
    s1 = Color.steps([ck, cg], steps=resolution, space=gamut)
    s2 = Color.steps([cr, cy], steps=resolution, space=gamut)
    fig.add_traces(render_rect_face(s1, s2, ('x', 'y'), space, gamut, resolution, opacity, edges))

    return fig


def plot_gamut_in_space(
    space,
    gamut,
    title="",
    dark=False,
    resolution=200,
    opacity=1.0,
    edges=False
):
    """Plot the given space in sRGB."""

    # Setup axis
    showbackground = True
    backgroundcolor = "rgb(230, 230, 230)"
    gridcolor = "rgb(255, 255, 255)"
    zerolinecolor = "rgb(255, 255, 255)"
    axis = dict(
        showbackground=showbackground,
        backgroundcolor=backgroundcolor,
        gridcolor=gridcolor,
        zerolinecolor=zerolinecolor,
    )

    # Setup plot layout
    layout = go.Layout(
        # General figure characteristics
        title=title,
        width=800,
        height=800,

        # Specify scene layout
        scene=go.layout.Scene(
            xaxis=go.layout.scene.XAxis(**axis),
            yaxis=go.layout.scene.YAxis(**axis),
            zaxis=go.layout.scene.ZAxis(**axis),
            aspectratio=dict(
                x=1, y=1, z=1
            ),
        ),

        # Control camera position
        # scene_camera = dict(
        #     eye=dict(x=2, y=2, z=0.1)
        # )
    )

    # Create figure to store the plot
    fig = go.Figure(layout=layout)

    # Render the space plot using a cylindrical space as the gamut space
    target = Color.CS_MAP[space]
    if not isinstance(target, Cylindrical) and not isinstance(target, Labish):
        return render_space_rect(fig, space, gamut, resolution, opacity, edges)
    else:
        return render_space_cyl(fig, space, gamut, resolution, opacity, edges)


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='3d_diagrams', description='Plot 3D gamut in a different color spaces.')
    parser.add_argument('--space', '-s', help='Desired space.')
    parser.add_argument(
        '--gamut',
        '-g',
        default='srgb',
        help=(
            'Gamut space to render space in. Gamut space must be bounded and must have channels in the range [0, 1].'
            'As only a shell is rendered for the gamut, the target space should be less than or equal to the size of '
            'the target gamut or there will be areas that do not render. Cylindrical spaces based specifically off '
            'an RGB gamut, such as HSL being based on sRGB, will only be done under the related gamut and will ignore '
            'this option.'
        )
    )
    parser.add_argument('--opacity', default=1.0, type=float, help="opacity")
    parser.add_argument(
        '--resolution', '-r',
        default="200",
        help=(
            "How densely to render the figure. Some spaces need higher resolution to flesh out certain areas, "
            "but it comes at the cost of speed."
        )
    )
    parser.add_argument('--edges', '-e', action="store_true", help="Plot edges.")
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    args = parser.parse_args()

    # Plot the color space
    fig = plot_gamut_in_space(
        args.space,
        args.gamut,
        title=args.title,
        dark=args.dark,
        resolution=int(args.resolution),
        opacity=args.opacity,
        edges=args.edges
    )

    # Show or save the data as an image, etc.
    fig.show()
    io.write_json(fig, 'fig.json')


if __name__ == "__main__":
    sys.exit(main())
