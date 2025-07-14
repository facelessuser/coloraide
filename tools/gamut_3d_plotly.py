"""Plot color space using Plotly."""
import sys
import argparse
from scipy.spatial import Delaunay
import plotly.graph_objects as go
import math
import plotly.io as io
import os
import json

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide.spaces import HSLish, HSVish, HWBish, Labish, LChish, RGBish  # noqa: E402
from coloraide import algebra as alg  # noqa: E402

FORCE_OWN_GAMUT = {'ryb', 'ryb-biased'}


def get_face_color(cmap, simplex, filters):
    """Get best color."""

    return Color.average([cmap[simplex[0]], cmap[simplex[1]], cmap[simplex[2]]], space='srgb').to_string(hex=True)


def create_custom_hsl(gamut):
    """Create a custom color object that has access to a special `hsl-gamut` space to map surface in."""

    cs = Color.CS_MAP[gamut]
    hsl = Color.CS_MAP['hsl']
    scale = not isinstance(cs, RGBish)

    class HSL(type(hsl)):
        NAME = f'-hsl-{gamut}'
        BASE = gamut
        GAMUT_CHECK = gamut
        CLIP_SPACE = None
        WHITE = cs.WHITE
        DYAMIC_RANGE = cs.DYNAMIC_RANGE
        INDEXES = cs.indexes()

        # Scale channels as needed
        OFFSET_1 = cs.channels[INDEXES[0]].low if scale else 0.0
        OFFSET_2 = cs.channels[INDEXES[1]].low if scale else 0.0
        OFFSET_3 = cs.channels[INDEXES[2]].low if scale else 0.0

        SCALE_1 = cs.channels[INDEXES[0]].high if scale else 1.0
        SCALE_2 = cs.channels[INDEXES[1]].high if scale else 1.0
        SCALE_3 = cs.channels[INDEXES[2]].high if scale else 1.0

        def to_base(self, coords):
            """Convert from RGB to HSL."""

            # Convert from HSL back to its original space
            coords = hsl.to_base(coords)
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
            return hsl.from_base(coords)

    class ColorCyl(Color):
        """Custom color."""

    ColorCyl.register(HSL())

    return ColorCyl


def create3d(fig, x, y, z, tri, cmap, edges, faces, ecolor, fcolor, opacity, filters):
    """Create the 3D renders."""

    i, j, k = tri.simplices.T
    if opacity:
        mesh = go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=i,
            j=j,
            k=k,
            vertexcolor=cmap if not faces else None,
            facecolor=[
                get_face_color(cmap, t, filters) if not fcolor else fcolor for t in tri.simplices
            ] if faces else None,
            flatshading = True,
            lighting = {"vertexnormalsepsilon": 0, "facenormalsepsilon": 0}
        )
        mesh.update(hoverinfo='skip')
        mesh.update(opacity=opacity)
        fig.add_traces([mesh])

    if edges:
        # Draw the triangles, but ensure they are separate by adding `None` to the end.
        xe = []
        ye = []
        ze = []
        tri_colors = []
        for p0, p1, p2 in tri.simplices:
            xe.extend([x[p0], x[p1], x[p2], x[p0], None])
            ye.extend([y[p0], y[p1], y[p2], y[p0], None])
            ze.extend([z[p0], z[p1], z[p2], z[p0], None])
            if ecolor is None:
                tri_colors.extend([cmap[p0], cmap[p1], cmap[p2], cmap[p0], '#000000'])

        # Use a single color for edges.
        if ecolor is not None:
            tri_colors = ecolor

        lines = go.Scatter3d(
            x=xe,
            y=ye,
            z=ze,
            mode='lines',
            marker={'size':0},
            showlegend=False,
            name='',
            line={'color': tri_colors}
        )
        lines.update(hoverinfo='skip')
        fig.add_traces([lines])


def cyl_disc(
    fig,
    ColorCyl,
    space,
    gamut,
    location,
    resolution,
    opacity,
    edges,
    faces,
    ecolor,
    fcolor,
    gmap,
    flags,
    filters
):
    """
    Plot cylindrical disc on either top or bottom of an RGB cylinder.

    Expectation is either a HSL, HSV, or HSB style cylinder.
    """

    cs = ColorCyl.CS_MAP[gamut]
    factor = cs.channels[1].high

    # Using a lightness of 0 can sometimes cause the bottom not to show with certain resolutions, so use a very
    # small value instead.
    zpos = 1e-16 if location == 'bottom' else 1.0 * factor

    x = []
    y = []
    z = []
    u = []
    v = []
    cmap = []

    # Interpolate a circle on the outer edge
    s1 = ColorCyl.steps(
        [ColorCyl(gamut, [hue, 1 * factor, 1 * zpos]) for hue in alg.linspace(0, 360, 2, endpoint=True)],
        steps=max(7, (resolution // 6) * 6 + 1),
        space=gamut,
        hue='specified'
    )
    s2 = ColorCyl(gamut, [alg.NaN, 1e-16, alg.NaN])

    # Interpolate concentric circles to the center of the disc
    step = int(resolution / 2)
    for r in range(step):
        for t1 in s1:
            s2['hue'] = t1['hue']
            c = t1.mix(s2, r / (step - 1), space=gamut, hue='specified')
            hue = c._space.hue_index()
            radius = c._space.radial_index()
            u.append(c[radius])
            v.append(c[hue])
            c.convert(space, norm=False, in_place=True)

            store_coords(c, x, y, z, flags)

            # Ensure colors fit in output color gamut.
            s = c.convert('srgb')
            if not s.in_gamut():
                s.fit(**gmap)
            else:
                s.clip()

            if filters:
                s.filter(filters[0], **filters[1], in_place=True, out_space=s.space()).clip()

            cmap.append(s.to_string(hex=True))

    # Calculate triangles
    tri = Delaunay([*zip(u, v)])

    create3d(fig, x, y, z, tri, cmap, edges, faces, ecolor, fcolor, opacity, filters)


def store_coords(c, x, y, z, flags):
    """Store coordinates."""

    # LCh spaces
    if flags['is_lchish']:
        light, chroma, hue = c._space.names()
        a, b = alg.polar_to_rect(c[chroma], c[hue])
        x.append(a)
        y.append(b)
        z.append(c[light])

    # HSL, HSV, or HWB spaces
    elif flags['is_hslish'] or flags['is_hsvish'] or flags['is_hwbish']:
        hue, sat, light = c._space.names()
        a, b = alg.polar_to_rect(c[sat], c[hue])
        x.append(a)
        y.append(b)
        z.append(c[light])

    # Any other generic cylindrical space that doesn't fit in the categories above.
    elif flags['is_cyl']:
        hue = c._space.hue_index()
        radius = c._space.radial_index()
        a, b = alg.polar_to_rect(c[radius], c[hue])
        x.append(a)
        y.append(b)
        z.append(c[3 - hue - radius])

    # Lab spaces
    elif flags['is_labish']:
        light, a, b = c._space.names()
        x.append(c[a])
        y.append(c[b])
        z.append(c[light])

    # Non-cylindrical spaces could be done here, but normally are not.
    else:
        x.append(c[0])
        y.append(c[1])
        z.append(c[2])


def render_space_cyl(fig, space, gamut, resolution, opacity, edges, faces, ecolor, fcolor, gmap, filters):
    """Renders the color space using an HSL cylinder that is then mapped to the given space."""

    target = Color.CS_MAP[space]
    flags = {
        'is_cyl': target.is_polar(),
        'is_labish': isinstance(target, Labish),
        'is_lchish': isinstance(target, LChish),
        'is_hslish': isinstance(target, HSLish),
        'is_hwbish': isinstance(target, HWBish),
        'is_hsvish': isinstance(target, HSVish)
    }

    # Determine the gamut mapping space to use.
    # Some spaces cannot be generalized (HWB and HPLuv for instance).
    if flags['is_hwbish']:
        ColorCyl = Color
        gspace = space
    elif Color.CS_MAP[gamut].is_polar():
        ColorCyl = Color
        gspace = gamut
    else:
        _gamut = space if space in FORCE_OWN_GAMUT else gamut
        ColorCyl = create_custom_hsl(_gamut)
        gspace = f'-hsl-{_gamut}'
    cs = ColorCyl.CS_MAP[gspace]

    # Adjust scaling factor if the mapping space requires it
    factor = cs.channels[1].high

    # Render the two halves of the cylinder
    u = []
    v = []
    x = []
    y = []
    z = []
    cmap = []

    # Interpolate the cylinder from 0 to 360 degrees.
    # Include, at the very least, 6 evenly spaced hues, and at higher resolutions
    # will include a multiple that will include the same 6 key points.
    # In HSL, this will cover all the corners of the RGB space.
    s1 = ColorCyl.steps(
        [ColorCyl(gspace, [hue, 1 * factor, 1 * factor]) for hue in alg.linspace(0, 360, 2, endpoint=True)],
        steps=max(7, (resolution // 6) * 6 + 1),
        space=gspace,
        hue='specified'
    )
    # A generic color at the bottom of the space which we can rotate for
    # interpolation by changing the hue.
    s2 = ColorCyl(gspace, [alg.NaN, 1 * factor, 1e-16])

    # Create a 3D mesh by interpolating ring at each lightness down the cylinder side.
    # Include at least 3 points of lightness: lightest, darkest, and mid, which in
    # HSL is the most colorful colors.
    for color in s1:
        s2['hue'] = color['hue']
        for c in ColorCyl.steps([color, s2], steps=max(3, (resolution // 2) * 2 + 1), space=gspace, hue='specified'):
            u.append(c[2])
            v.append(c['hue'])
            c.convert(space, norm=False, in_place=True)

            store_coords(c, x, y, z, flags)

            # Adjust gamut to fit the display space
            s = c.convert('srgb')
            if not s.in_gamut():
                s.fit(**gmap)
            else:
                s.clip()

            if filters:
                s.filter(filters[0], **filters[1], in_place=True, out_space=s.space()).clip()

            cmap.append(s.to_string(hex=True))

    # Calculate the triangles
    tri = Delaunay([*zip(u, v)])

    create3d(fig, x, y, z, tri, cmap, edges, faces, ecolor, fcolor, opacity, filters)

    # Generate tops for spaces that do not normally get tops automatically.
    if flags['is_hwbish'] or (flags['is_cyl'] and not flags['is_lchish']) or isinstance(cs, HSVish):
        cyl_disc(
            fig, ColorCyl, space, gspace, 'top', resolution, opacity, edges, faces, ecolor, fcolor, gmap, flags, filters
        )
    cyl_disc(
        fig, ColorCyl, space, gspace, 'bottom', resolution, opacity, edges, faces, ecolor, fcolor, gmap, flags, filters
    )

    return fig


def plot_gamut_in_space(
    space,
    gamuts,
    title="",
    dark=False,
    gmap=None,
    size=(800, 800),
    camera=None,
    aspect=None,
    projection='perspective',
    filters=()
):
    """Plot the given space in sRGB."""

    if gmap is None:
        gmap = {}

    io.templates.default = 'plotly_dark' if dark else 'plotly'

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
    is_cyl = target.is_polar()
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
    axis = {
        "showbackground": showbackground,
        "backgroundcolor": backgroundcolor,
        "gridcolor": gridcolor,
        "zerolinecolor": zerolinecolor,
    }
    xaxis = str(names[axm[0]]) if not is_cyl else f"{names[axm[0]]} (0˚ - 360˚)"
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
        scene_camera={
            "projection": go.layout.scene.camera.Projection(type=projection),
            "center": {"x": 0, "y": 0, "z": 0},
            "up": {"x": 0, "y": 0, "z": 1},
            "eye": {"x": x, "y": y, "z": z}
        }
    )

    # Create figure to store the plot
    fig = go.Figure(layout=layout)

    for gamut, config in gamuts.items():
        opacity = config.get('opacity', 1)
        resolution = config.get('resolution', 200)
        edges = config.get('edges', False)
        ecolor = None
        if isinstance(edges, str):
            c = Color(edges).convert('srgb').fit(**gmap)
            if filters:
                c.filter(filters[0], **filters[1], in_place=True, out_space=c.space()).clip()
            ecolor = c.to_string(hex=True, alpha=False)
            edges = True
        faces = config.get('faces', False)
        fcolor = ''
        if isinstance(faces, str):
            c = Color(faces).convert('srgb').fit(**gmap)
            if filters:
                c.filter(filters[0], **filters[1], in_place=True, out_space=c.space()).clip()
            fcolor = c.to_string(hex=True, alpha=False)
            faces = True

        render_space_cyl(fig, space, gamut, resolution, opacity, edges, faces, ecolor, fcolor, gmap, filters)

    return fig


def plot_colors(fig, space, gamut, gmap_colors, colors, gmap, filters=()):
    """Plot gamut mapping."""

    if not gmap_colors and not colors:
        return

    gamut_mapping = gmap_colors.split(';') if gmap_colors.strip() else []
    non_mapped = colors.split(';') if colors.strip() else []
    if gamut_mapping or non_mapped:
        target = Color.CS_MAP[space]
        flags = {
            'is_cyl': target.is_polar(),
            'is_labish': isinstance(target, Labish),
            'is_lchish': isinstance(target, LChish),
            'is_hslish': isinstance(target, HSLish),
            'is_hwbish': isinstance(target, HWBish),
            'is_hsvish': isinstance(target, HSVish)
        }

        l = len(gamut_mapping)
        for i, c in enumerate(gamut_mapping + non_mapped):
            c1 = Color(c)
            c2 = Color(c).fit(gamut, **gmap)
            c1.convert(space, in_place=True)
            c2.convert(space, in_place=True)
            x = []
            y = []
            z = []
            for c in ([c1, c2] if i < l else [c1]):
                store_coords(c, x, y, z, flags)

            c2.convert('srgb', in_place=True).fit(**gmap)
            if filters:
                c2.filter(filters[0], **filters[1], in_place=True, out_space=c2.space()).clip()

            fig.add_trace(
                go.Scatter3d(
                    x=x, y=y, z=z,
                    line={'color': 'black', 'width': 2},
                    marker={
                        'color': c2.to_string(hex=True, alpha=False),
                        'size': [16, 0],
                        'opacity': 1,
                        'line': {'width': 2}
                    },
                    showlegend=False
                )
            )


def plot_interpolation(
    fig,
    space,
    interp_colors,
    interp_method,
    gmap,
    simulate_alpha,
    interp_gmap,
    filters=()
):
    """Plot interpolations."""

    if not interp_colors:
        return

    colors = Color.steps(
        interp_colors.split(';'),
        **interp_method
    )

    target = Color.CS_MAP[space]
    flags = {
        'is_cyl': target.is_polar(),
        'is_labish': isinstance(target, Labish),
        'is_lchish': isinstance(target, LChish),
        'is_hslish': isinstance(target, HSLish),
        'is_hwbish': isinstance(target, HWBish),
        'is_hsvish': isinstance(target, HSVish)
    }

    x = []
    y = []
    z = []
    cmap = []
    for c in colors:
        c.convert(space, in_place=True)
        if interp_gmap:
            c.fit('srgb', **gmap)
        store_coords(c, x, y, z, flags)
        c.convert('srgb', in_place=True)
        c.fit(**gmap)
        if filters:
            c.filter(filters[0], **filters[1], in_place=True, out_space=c.space()).clip()
        if simulate_alpha:
            cmap.append(Color.layer([c, 'white'], space='srgb').to_string(hex=True, alpha=False))
        else:
            cmap.append(c.to_string(hex=True, alpha=False))

    trace = go.Scatter3d(
        x=x, y=y, z=z,
        mode = 'markers',
        marker={'color': cmap, 'opacity': 1},
        showlegend=False
    )

    fig.add_trace(trace)


def plot_harmony(
    fig,
    space,
    harmony,
    gmap,
    simulate_alpha,
    harmony_gmap,
    filters=()
):
    """Plot color harmony."""

    if not harmony:
        return

    hcolor, options = harmony
    if 'space' not in options:
        options['space'] = space
    options['out_space'] = space

    colors = Color(hcolor).harmony(**options)

    target = Color.CS_MAP[space]
    flags = {
        'is_cyl': target.is_polar(),
        'is_labish': isinstance(target, Labish),
        'is_lchish': isinstance(target, LChish),
        'is_hslish': isinstance(target, HSLish),
        'is_hwbish': isinstance(target, HWBish),
        'is_hsvish': isinstance(target, HSVish)
    }

    cmap = []
    x = []
    y = []
    z = []
    for s in colors:
        c = s.normalize(nans=False)
        if harmony_gmap:
            c.fit('srgb', **gmap)
        store_coords(c, x, y, z, flags)
        c.convert('srgb', in_place=True).fit(**gmap)
        if filters:
            c.filter(filters[0], **filters[1], in_place=True, out_space=c.space()).clip()
        if simulate_alpha:
            cmap.append(Color.layer([c, 'white'], space='srgb').to_string(hex=True, alpha=False))
        else:
           cmap.append(c.to_string(hex=True, alpha=False))

    if options['name'] in ('wheel', 'rectangle', 'square', 'triad'):
        x.append(x[0])
        y.append(y[0])
        z.append(z[0])
        cmap.append(cmap[0])
        size = ([8] * (len(x) - 1)) + [0]
    else:
        size = [8] * len(x)

    trace = go.Scatter3d(
        x=x, y=y, z=z,
        marker={'size': size, 'color': cmap, 'opacity': 1},
        line={'color': 'black', 'width': 3},
        showlegend=False
    )

    fig.add_trace(trace)


def plot_average(
    fig,
    space,
    avg_colors,
    avg_options,
    gmap,
    simulate_alpha,
    avg_gmap,
    filters=()
):
    """Plot interpolations."""

    if not avg_colors:
        return

    parts = avg_colors.split(':')

    colors = parts[0].split(';')
    if len(parts) == 2:
        weights = [float(i.strip()) for i in parts[1].split(',')]
    else:
        weights = None

    color = Color.average(
        colors,
        weights,
        space=avg_options['space']
    )

    target = Color.CS_MAP[space]
    flags = {
        'is_cyl': target.is_polar(),
        'is_labish': isinstance(target, Labish),
        'is_lchish': isinstance(target, LChish),
        'is_hslish': isinstance(target, HSLish),
        'is_hwbish': isinstance(target, HWBish),
        'is_hsvish': isinstance(target, HSVish)
    }

    for s in colors:
        x = []
        y = []
        z = []
        cmap = []
        c = Color(s).convert(space, in_place=True).normalize(nans=False)
        if avg_gmap:
            c.fit('srgb', **gmap)
        store_coords(c, x, y, z, flags)
        c.convert('srgb', in_place=True).fit(**gmap)
        if filters:
            c.filter(filters[0], **filters[1], in_place=True, out_space=c.space()).clip()
        if simulate_alpha:
            cmap.append(Color.layer([c, 'white'], space='srgb').to_string(hex=True, alpha=False))
        else:
           cmap.append(c.to_string(comma=True, alpha=False))

        c = Color(color).convert(space, in_place=True).normalize(nans=False)
        if avg_gmap:
            c.fit('srgb', **gmap)
        store_coords(c, x, y, z, flags)
        c.convert('srgb', in_place=True).fit(**gmap)
        if filters:
            c.filter(filters[0], **filters[1], in_place=True, out_space=c.space()).clip()
        if simulate_alpha:
            cmap.append(Color.layer([c, 'white'], space='srgb').to_string(hex=True, alpha=False))
        else:
            cmap.append(c.to_string(hex=True, alpha=False))

        trace = go.Scatter3d(
            x=x, y=y, z=z,
            marker={'size': [8, 16], 'color': cmap, 'opacity': 1},
            line={'color': cmap[0], 'width': 3},
            showlegend=False
        )

        fig.add_trace(trace)


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='3d_diagrams', description='Plot 3D gamut in a different color spaces.')
    parser.add_argument('--space', '-s', help='Desired space.')

    # Gamut and gamut mapping
    parser.add_argument(
        '--gamut',
        '-g',
        action='append',
        default=[],
        help=(
            "Gamut space to render space in. Can be followed by a JSON config in the form 'space:{}' to set `edges`,"
            '`faces`, `opacity`, or `resolution`. `edges` and `faces` can be a boolean to disable or enable them or '
            'color to configure them all as a specific color.'
        )
    )
    parser.add_argument(
        '--gmap',
        default='raytrace',
        help=(
            "Gamut mapping algorithm. To set additional options, follow the algorithm with with a JSON string and "
            "containing the parameters in the form of 'algorithm:{}'."
        )
    )
    parser.add_argument('--gmap-colors', default='', help='Color(s) to gamut map, separated by semicolons.')
    parser.add_argument(
        '--colors',
        default='',
        help='Plot arbitrary color points. Colors are separated with semicolons.'
    )

    # Interpolation visualization
    parser.add_argument(
        '--avg-colors',
        default='',
        help="Colors that should be averaged together separated by semicolons."
    )
    parser.add_argument(
        '--average-options',
        default='{}',
        help=(
            "Averaging configuration (JSON string)."
        )
    )

    parser.add_argument('--interp-colors', default='', help='Interpolation colors separated by semicolons.')
    parser.add_argument(
        '--interp-method',
        default='linear',
        help=(
            "Interpolation configuration. Interpolation method followed by an optional JSON containing options: "
            "'method: {}'"
        )
    )
    parser.add_argument(
        '--harmony',
        default='',
        help=(
            "Harmony configuration: 'color:harmony'. Harmony can be followed by an optional JSON containing options: "
            "'color:harmony: {}'"
        )
    )
    parser.add_argument(
        '--mix-alpha',
        action='store_true',
        help="Simulate interpolation/averaging/harmony opacity by overlaying on white."
    )
    parser.add_argument(
        '--mix-gmap',
        action='store_true',
        help="Force plotted interpolation/averaging/harmony results to be gamut mapped."
    )

    parser.add_argument(
        '--filter',
        default='',
        help=(
            "Apply filter. Filter options can be provided as a JSON string after filter name: 'filter:{}'."
        )
    )

    # Graphical and plotting options
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--height', '-H', type=int, default=800, help="Height")
    parser.add_argument('--width', '-W', type=int, default=800, help="Width")

    # Camera and perspective
    parser.add_argument('--pos', '-p', default=None, help="Position of camara 'x:y:z'")
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

    gamuts = {}
    first = None
    for gamut in args.gamut:
        parts = [p.strip() if not e else json.loads(p) for e, p in enumerate(gamut.split(':', 1))]
        gamuts[parts[0]] = {} if len(parts) == 1 else parts[1]
        first = parts[0]
    if first is None:
        first = 'srgb'
        gamuts['srgb'] = {}

    aspect = {k: float(v) for k, v in zip(['x', 'y', 'z'], args.aspect_ratio.split(':'))}
    parts = [p.strip() if not e else json.loads(p) for e, p in enumerate(args.gmap.split(':', 1))]
    gmap = {'method': parts[0]}
    if len(parts) == 2:
        gmap.update(parts[1])

    filters = []
    if args.filter:
        parts = [p.strip() if not e else json.loads(p) for e, p in enumerate(args.filter.split(':', 1))]
        filters.append(parts[0])
        if len(parts) == 2:
            filters.append(parts[1])
        else:
            filters.append({})

    # Plot the color space(s)
    fig = plot_gamut_in_space(
        args.space,
        gamuts,
        title=args.title,
        dark=args.dark,
        gmap=gmap,
        size=(args.width, args.height),
        camera={'a': args.azimuth, 'e': args.elevation, 'r': args.distance},
        aspect=aspect,
        projection=args.projection,
        filters=filters
    )

    parts = [p.strip() if not e else json.loads(p) for e, p in enumerate(args.interp_method.split(':', 1))]
    interp = {'method': parts[0], 'hue': 'shorter', 'steps': 100}
    if len(parts) == 2:
        interp.update(parts[1])

    # Plot interpolation
    plot_interpolation(
        fig,
        args.space,
        args.interp_colors,
        interp,
        gmap,
        args.mix_alpha,
        args.mix_gmap,
        filters
    )

    avg_options = {"space": "srgb-linear"}
    avg_options.update(json.loads(args.average_options))
    plot_average(
        fig,
        args.space,
        args.avg_colors,
        avg_options,
        gmap,
        args.mix_alpha,
        args.mix_gmap,
        filters
    )

    parts = [p.strip() if e < 2 else json.loads(p) for e, p in enumerate(args.harmony.split(':', 2)) if p]
    harmony_config = []
    if parts:
        hcolor = parts[0]
        harmony = {'name': parts[1]}
        if len(parts) == 3:
            harmony.update(parts[2])
        harmony_config = [hcolor, harmony]

    plot_harmony(
        fig,
        args.space,
        harmony_config,
        gmap,
        args.mix_alpha,
        args.mix_gmap,
        filters
    )

    # Plot gamut mapping examples
    plot_colors(fig, args.space, first, args.gmap_colors, args.colors, gmap, filters)

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
                    f.write(fig.to_image(format=filetype, width=args.width, height=args.height))
        else:
            fig.show('browser')
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
