"""Plot color space using Plotly."""
import sys
import argparse
from scipy.spatial import Delaunay
from plotly.figure_factory import create_trisurf as trisurf
import plotly.graph_objects as go
import math
import plotly.io as io
import os

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide.spaces import HSLish, HSVish, Cylindrical, Labish, LChish, RGBish  # noqa: E402
from coloraide import algebra as alg  # noqa: E402

FORCE_RECT = ('cmy',)


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


def get_face_color(cmap, simplex):
    """Get best color."""

    return Color.average([cmap[simplex[0]], cmap[simplex[1]], cmap[simplex[2]]], space='srgb').to_string(hex=True)


def cyl_disc(ColorCyl, space, gamut, location, resolution, opacity, edges):
    """
    Plot cylindrical disc on either top or bottom of an RGB cylinder.

    Expectation is either a HSL, HSV, or HSB style cylinder.
    """

    cs = ColorCyl.CS_MAP[space]
    if isinstance(cs, (HSVish, HSLish)):
        space_type = 'hslish/hsvish'
    else:
        space_type = space
    gspace = ColorCyl.CS_MAP[gamut]
    factor = gspace.channels[1].high

    zpos = 0.0 if location == 'bottom' else 1.0 * factor
    # HWB bottom disc will have a single point in the center that is a different colors at different hues. The mesh will
    # resolve one of them as the center, usually red. This will cause color averaging in the center of the disc to be
    # red-ish for all colors in the center. At lower resolutions, this is more noticeable. To avoid this, interpolate
    # rings very close to zero radius, but not zero radius. The mesh will still connect all the points near the center,
    # but it will be too small to see.
    start, end = 1.0 * factor, (1e-6 if space == 'hwb' and location == 'bottom' else 0.0)

    # Render the two halves of the disc
    hue_start, hue_end = 0, 360
    x = []
    y = []
    z = []
    u = []
    v = []
    cmap = []

    # Interpolate a circle on the outer edge
    c1 = ColorCyl(gamut, [hue_start, start, zpos])
    c2 = ColorCyl(gamut, [hue_end, start, zpos])
    chan_name = str(c1._space.channels[1])
    s1 = ColorCyl.steps([c1, c2], steps=resolution, space=gamut, hue='specified')
    s2 = [t.clone().set(chan_name, end) for t in s1]

    # Interpolate concentric circles to the center of the disc
    step = int(resolution / 2)
    for r in range(step):
        for t1, t2 in zip(s1, s2):
            c = t1.mix(t2, r / (step - 1), space=gamut, hue='specified')
            hue = c._space.hue_index()
            a, b = alg.polar_to_rect(c[1], c[hue])
            u.append(a)
            v.append(b)
            c.convert(space, norm=False, in_place=True)

            # HSL and HSV spaces
            if space_type == 'hslish/hsvish':
                hue, saturation, lightness = c._space.indexes()
                a, b = alg.polar_to_rect(c[saturation], c[hue])
                x.append(a)
                y.append(b)
                z.append(c[lightness])

            # HWB
            else:
                hue = c._space.hue_index()
                a, b = alg.polar_to_rect(c[1], c[hue])
                x.append(a)
                y.append(b)
                z.append(c[2])

            # Ensure colors fit in output color gamut.
            s = c.convert('srgb')
            if not s.in_gamut():
                s.fit()
            else:
                s.clip()
            cmap.append(s)

    # Calculate triangles
    tri = Delaunay(list(zip(u, v)))

    # Generate triangulated surface
    trace = trisurf(
        x=x, y=y, z=z,
        simplices=tri.simplices,
        show_colorbar=False,
        plot_edges=edges,
        color_func=[get_face_color(cmap, t) for t in tri.simplices]
    ).data
    trace[0].update(opacity=opacity)
    if edges:
        trace[1].update(hoverinfo='skip')

    return trace


def render_space_cyl(fig, space, gamut, resolution, opacity, edges):
    """
    Renders the color space using an RGB cylinder that is then mapped to the given space.

    Ideally used to represent cylindrical spaces and will align the the lightness equivalent
    as the Z axis. Lab-ish colors are performed in the mode as they are essentially cylindrical
    with the chroma and hue converted to Cartesian a and b.
    """

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

    # Render the two halves of the cylinder
    start, end = 0, 360
    u = []
    v = []
    x = []
    y = []
    z = []
    cmap = []

    # Interpolate the cylinder from 0 to 360 degrees
    c1 = ColorCyl(gamut_space, [start, 1 * factor, 1 * factor])
    c2 = ColorCyl(gamut_space, [start, 1 * factor, 0])
    c3 = ColorCyl(gamut_space, [end, 1 * factor, 1 * factor])
    c4 = ColorCyl(gamut_space, [end, 1 * factor, 0])
    s1 = ColorCyl.steps([c1, c2], steps=resolution, space=gamut_space, hue='specified')
    s2 = ColorCyl.steps([c3, c4], steps=resolution, space=gamut_space, hue='specified')

    # Create a 3D mesh by interpolating ring at each lightness down the cylinder side.
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

            # Adjust gamut to fit the display space
            s = c.convert('srgb')
            if not s.in_gamut():
                s.fit()
            else:
                s.clip()

            cmap.append(s)

    # Calculate the triangles
    tri = Delaunay(list(zip(u, v)))

    # Build the triangulated surface
    trace = trisurf(
        x=x, y=y, z=z,
        simplices=tri.simplices,
        show_colorbar=False,
        plot_edges=edges,
        color_func=[get_face_color(cmap, t) for t in tri.simplices]
    ).data
    trace[0].update(opacity=opacity)
    if edges:
        trace[1].update(hoverinfo='skip')
    fig.add_traces(trace)

    # Generate tops for spaces that do not normally get tops automatically.
    if space in ('hwb', 'hpluv'):
        fig.add_traces(cyl_disc(ColorCyl, space, gamut_space, 'top', resolution, opacity, edges))

    if is_cyl and not is_labish and not is_lchish:
        # We normally get a bottom except in the case of HWB.
        fig.add_traces(cyl_disc(ColorCyl, space, gamut_space, 'bottom', resolution, opacity, edges))

    return fig


def render_rect_face(s1, s2, dim, space, gamut, resolution, opacity, edges):
    """Render the RGB rectangular face."""

    x = []
    y = []
    z = []
    X = []
    Y = []
    Z = []
    cmap = []

    # Render an RGB face by taking two interpolated sides and interpolating the points across the face
    for c1, c2 in zip(s1, s2):
        for t in Color.steps([c1, c2], steps=int(resolution / 4), space=gamut):
            x.append(t[0])
            y.append(t[1])
            z.append(t[2])
            t.convert(space, norm=False, in_place=True)
            X.append(t[0])
            Y.append(t[1])
            Z.append(t[2])

            # Fit colors to output gamut
            s = t.convert('srgb')
            if not s.in_gamut():
                s.fit()
            else:
                s.clip()
            cmap.append(s)

    # Calculate triangles
    tri = Delaunay(list(zip(locals().get(dim[0]), locals().get(dim[1]))))

    # Generate triangulated surface
    trace = trisurf(
        x=X, y=Y, z=Z,
        simplices=tri.simplices,
        show_colorbar=False,
        plot_edges=edges,
        color_func=[get_face_color(cmap, t) for t in tri.simplices]
    ).data
    trace[0].update(opacity=opacity)
    if edges:
        trace[1].update(hoverinfo='skip')

    return trace


def render_space_rect(fig, space, gamut, resolution, opacity, edges):
    """Render rectangular space."""

    # Six corners of the RGB cube
    ck = Color(gamut, [0, 0, 0])
    cw = Color(gamut, [1, 1, 1])
    cr = Color(gamut, [1, 0, 0])
    cg = Color(gamut, [0, 1, 0])
    cb = Color(gamut, [0, 0, 1])
    cy = Color(gamut, [1, 1, 0])
    cc = Color(gamut, [0, 1, 1])
    cm = Color(gamut, [1, 0, 1])

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
    edges=False,
    size=(800, 800),
    camera=None,
    aspect=None,
    projection='perspective'
):
    """Plot the given space in sRGB."""

    io.templates.default = 'plotly_dark' if dark else 'plotly'

    # I have no idea why this number causes HSL to lose its bottom
    if resolution == 50:
        resolution = 51

    if camera is None:
        camera = {'a': 45, 'e': 45, 'r': math.sqrt(1.25 ** 2 + 1.25 ** 2 + 1.25 ** 2)}

    a = math.radians((90 - camera['a']) % 360)
    e = math.radians(90 - camera['e'])
    r = camera['r']
    y = r * math.sin(e) * math.cos(a)
    x = r * math.sin(e) * math.sin(a)
    z = r * math.cos(e)

    if aspect is None:
        aspect = {'x': 1, 'y': 1, 'z': 1}

    # Get names for
    target = Color.CS_MAP[space]
    if len(target.CHANNELS) > 3:
        print('Color spaces with dimensions greater than 3 are not supported')
        return None

    names = target.CHANNELS
    is_rgbish = isinstance(target, RGBish)
    is_cyl = isinstance(target, Cylindrical)
    is_labish = isinstance(target, Labish)
    is_lchish = isinstance(target, LChish)
    is_hslish_hsvish = isinstance(target, (HSLish, HSVish))

    # Setup axes
    if is_labish:
        c1, c2, c3 = target.indexes()
        axm = [c2, c3, c1]
    elif is_lchish:
        c1, c2, c3 = target.indexes()
        axm = [c3, c2, c1]
    elif is_hslish_hsvish:
        axm = [0, 1, 2]
    else:
        axm = [0, 1, 2]

    showbackground = True
    backgroundcolor = "rgb(230, 230, 230)" if not dark else '#282830'
    gridcolor = "rgb(255, 255, 255)" if not dark else '#111'
    zerolinecolor = "rgb(255, 255, 255)" if not dark else '#111'
    axis = dict(
        showbackground=showbackground,
        backgroundcolor=backgroundcolor,
        gridcolor=gridcolor,
        zerolinecolor=zerolinecolor,
    )
    xaxis = str(names[axm[0]]) if not is_cyl else "{} (0˚ - 360˚)".format(names[axm[0]])
    yaxis = str(names[axm[1]])
    zaxis = str(names[axm[2]])

    # Setup plot layout
    layout = go.Layout(
        # General figure characteristics
        title=title,
        width=size[0],
        height=size[1],

        # Specify scene layout
        scene=go.layout.Scene(
            xaxis=go.layout.scene.XAxis(title=xaxis, showticklabels=not is_cyl, **axis),
            yaxis=go.layout.scene.YAxis(title=yaxis, **axis),
            zaxis=go.layout.scene.ZAxis(title=zaxis, **axis),
            aspectratio=aspect
        ),

        # Control camera position
        scene_camera=dict(
            projection=go.layout.scene.camera.Projection(type=projection),
            center=dict(x=0, y=0, z=0),
            up=dict(x=0, y=0, z=1),
            eye=dict(x=x, y=y, z=z)
        )
    )

    # Create figure to store the plot
    fig = go.Figure(layout=layout)

    target = Color.CS_MAP[space]
    if is_rgbish or space in FORCE_RECT:
        # Use a rectangular space for RGB-ish spaces to give a sharper cube
        return render_space_rect(fig, space, gamut, resolution, opacity, edges)
    else:
        # Render the space plot using a cylindrical space as the gamut space
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
            "but it comes at the cost of speed. Minimum is 60, default is 200."
        )
    )
    parser.add_argument('--pos', '-p', default=None, help="Position of camara 'x:y:z'")
    parser.add_argument('--edges', '-e', action="store_true", help="Plot edges.")
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--height', '-H', type=int, default=800, help="Height")
    parser.add_argument('--width', '-W', type=int, default=800, help="Width")
    parser.add_argument('--azimuth', '-A', type=float, default=45, help="Camera X position")
    parser.add_argument('--elevation', '-E', type=float, default=45, help="Camera Y position")
    parser.add_argument('--distance', '-D', type=float, default=2.5, help="Camera Z position")
    parser.add_argument(
        '--aspect-ratio', '-R',
        default='1:1:1',
        help="Aspect ratio. Set to 0:0:0 to leave aspect ratio untouched."
    )
    parser.add_argument(
        '--projection', '-P',
        default='perspective',
        help="Projection mode, perspective or orthographic"
    )
    args = parser.parse_args()

    aspect = {k: float(v) for k, v in zip(['x', 'y', 'z'], args.aspect_ratio.split(':'))}

    # Plot the color space
    fig = plot_gamut_in_space(
        args.space,
        args.gamut,
        title=args.title,
        dark=args.dark,
        resolution=max(8, int(args.resolution)),
        opacity=args.opacity,
        edges=args.edges,
        size=(args.width, args.height),
        camera={'a': args.azimuth, 'e': args.elevation, 'r': args.distance},
        aspect=aspect,
        projection=args.projection
    )

    # Show or save the data as an image, etc.
    if fig:
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
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
