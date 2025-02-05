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
from coloraide.spaces import HSLish, HSVish, HWBish, Labish, LChish, Regular  # noqa: E402
from coloraide import algebra as alg  # noqa: E402
from coloraide.spaces.hsl import hsl_to_srgb, srgb_to_hsl  # noqa: E402

FORCE_OWN_GAMUT = {'ryb', 'ryb-biased'}
CYL_GAMUT = {'hpluv', 'okhsl', 'okhsv'}


def get_face_color(cmap, simplex):
    """Get best color."""

    return Color.average([cmap[simplex[0]], cmap[simplex[1]], cmap[simplex[2]]], space='srgb').to_string(hex=True)


def create_custom_hsl(gamut):
    """Create a custom color object that has access to a special `hsl-gamut` space to map surface in."""

    cs = Color.CS_MAP[gamut]

    class HSL(type(Color.CS_MAP['hsl'])):
        NAME = f'-hsl-{gamut}'
        BASE = gamut
        GAMUT_CHECK = gamut
        CLIP_SPACE = None
        WHITE = cs.WHITE
        DYAMIC_RANGE = cs.DYNAMIC_RANGE

    class ColorCyl(Color):
        """Custom color."""

    ColorCyl.register(HSL())

    return ColorCyl


def create_custom_rgb(gamut):
    """
    Create a custom color RGB space from an HSL like color space.

    This allows us to handle something like HPLuv as a gamut when rendering rectangular color spaces.

    Will likely only work for some color spaces.
    """

    cs = Color.CS_MAP[gamut]

    class RGB(type(Color.CS_MAP['srgb-linear'])):
        """Custom RGB class."""

        NAME = f'-rgb-{gamut}'
        BASE = gamut
        GAMUT_CHECK = gamut
        CLIP_SPACE = None
        WHITE = cs.WHITE
        DYAMIC_RANGE = cs.DYNAMIC_RANGE
        INDEXES = cs.indexes()
        SCALE_SAT = cs.CHANNELS[INDEXES[1]].high
        SCALE_LIGHT = cs.CHANNELS[INDEXES[1]].high

        def to_base(self, coords):  # noqa: N804 # Faulty lint error
            """Convert from RGB to HSL."""

            coords = srgb_to_hsl(coords)
            if self.SCALE_SAT != 1:
                coords[1] *= self.SCALE_SAT
            if self.SCALE_LIGHT != 1:
                coords[2] *= self.SCALE_LIGHT
            ordered = [0.0, 0.0, 0.0]
            for e, c in enumerate(coords):
                ordered[self.INDEXES[e]] = c
            return ordered

        def from_base(self, coords):  # noqa: N804 # Faulty lint error
            """Convert from HSL to RGB."""

            coords = [coords[i] for i in self.INDEXES]
            if self.SCALE_SAT != 1:
                coords[1] /= self.SCALE_SAT
            if self.SCALE_LIGHT != 1:
                coords[2] /= self.SCALE_LIGHT
            coords = hsl_to_srgb(coords)
            return coords

    class ColorRGB(Color):
        """Custom color."""

    ColorRGB.register(RGB())

    return ColorRGB


def create3d(fig, x, y, z, tri, cmap, edges, faces, ecolor, fcolor, opacity):
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
            facecolor=[get_face_color(cmap, t) if not fcolor else fcolor for t in tri.simplices] if faces else None
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


def cyl_disc(fig, ColorCyl, space, gamut, location, resolution, opacity, edges, faces, ecolor, fcolor, gmap):
    """
    Plot cylindrical disc on either top or bottom of an RGB cylinder.

    Expectation is either a HSL, HSV, or HSB style cylinder.
    """

    cs = ColorCyl.CS_MAP[space]
    is_hwbish = isinstance(cs, HWBish)
    if is_hwbish or isinstance(cs, (HSVish, HSLish)):
        space_type = 'rgb_cyl'
    else:
        space_type = space
    gspace = ColorCyl.CS_MAP[gamut]
    factor = gspace.channels[1].high

    zpos = 0.0 if location == 'bottom' else 1.0 * factor
    # HWB bottom disc will have a single point in the center that is a different colors at different hues. The mesh will
    # resolve one of them as the center, usually red. This will cause color averaging in the center of the disc to be
    # reddish for all colors in the center. At lower resolutions, this is more noticeable. To avoid this, interpolate
    # rings very close to zero radius, but not zero radius. The mesh will still connect all the points near the center,
    # but will leave a small hole at the center which will be too small to see.
    start, end = 1.0 * factor, (1e-6 if is_hwbish and location == 'bottom' else 0.0)

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
            radius = c._space.radial_index()
            a, b = alg.polar_to_rect(c[radius], c[hue])
            u.append(a)
            v.append(b)
            c.convert(space, norm=False, in_place=True)

            # HSL, HSV. and HWB spaces
            if space_type == 'rgb_cyl':
                hue, saturation, lightness = c._space.indexes()
                a, b = alg.polar_to_rect(c[saturation], c[hue])
                x.append(a)
                y.append(b)
                z.append(c[lightness])

            # Any other generic cylindrical space
            else:
                hue = c._space.hue_index()
                radius = c._space.radial_index()
                a, b = alg.polar_to_rect(c[radius], c[hue])
                x.append(a)
                y.append(b)
                z.append(c[3 - hue - radius])

            # Ensure colors fit in output color gamut.
            s = c.convert('srgb')
            if not s.in_gamut():
                s.fit(**gmap)
            else:
                s.clip()

            cmap.append(s.to_string(hex=True))

    # Calculate triangles
    tri = Delaunay(list(zip(u, v)))

    create3d(fig, x, y, z, tri, cmap, edges, faces, ecolor, fcolor, opacity)


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


def render_space_cyl(fig, space, gamut, resolution, opacity, edges, faces, ecolor, fcolor, gmap):
    """
    Renders the color space using an RGB cylinder that is then mapped to the given space.

    Ideally used to represent cylindrical spaces and will align the lightness equivalent
    as the Z axis. Lab-ish colors are performed in the mode as they are essentially cylindrical
    with the chroma and hue converted to Cartesian a and b.
    """

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
    if flags['is_hwbish'] or space in FORCE_OWN_GAMUT:
        ColorCyl = Color
        gamut_space = space
    elif gamut in CYL_GAMUT:
        ColorCyl = Color
        gamut_space = gamut
    else:
        ColorCyl = create_custom_hsl(gamut)
        gamut_space = f'-hsl-{gamut}'
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

            store_coords(c, x, y, z, flags)

            # Adjust gamut to fit the display space
            s = c.convert('srgb')
            if not s.in_gamut():
                s.fit(**gmap)
            else:
                s.clip()

            cmap.append(s.to_string(hex=True))

    # Calculate the triangles
    tri = Delaunay(list(zip(u, v)))

    create3d(fig, x, y, z, tri, cmap, edges, faces, ecolor, fcolor, opacity)

    # Generate tops for spaces that do not normally get tops automatically.
    if flags['is_hwbish'] or space in CYL_GAMUT:
        cyl_disc(fig, ColorCyl, space, gamut_space, 'top', resolution, opacity, edges, faces, ecolor, fcolor, gmap)

    if flags['is_cyl'] and not flags['is_labish'] and not flags['is_lchish']:
        # We normally get a bottom except in the case of HWB.
        cyl_disc(fig, ColorCyl, space, gamut_space, 'bottom', resolution, opacity, edges, faces, ecolor, fcolor, gmap)

    return fig


def render_rect_face(fig, colorrgb, s1, s2, dim, space, gamut, resolution, opacity, edges, faces, ecolor, fcolor, gmap):
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
        for t in colorrgb.steps([c1, c2], steps=int(resolution / 4), space=gamut):
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
                s.fit(**gmap)
            else:
                s.clip()
            cmap.append(s.to_string(hex=True))

    # Calculate triangles
    tri = Delaunay(list(zip(locals().get(dim[0]), locals().get(dim[1]))))
    create3d(fig, X, Y, Z, tri, cmap, edges, faces, ecolor, fcolor, opacity)


def render_space_rect(fig, space, gamut, res, opacity, edges, faces, ecolor, fcolor, gmap):
    """Render rectangular space."""

    if space in FORCE_OWN_GAMUT:
        gamut = space

    cs = Color.CS_MAP[gamut]
    if isinstance(cs, HSLish):
        colorrgb = create_custom_rgb(gamut)
        gamut = f'-rgb-{gamut}'
    else:
        colorrgb = Color

    # Six corners of the RGB cube
    ck = colorrgb(gamut, [0, 0, 0])
    cw = colorrgb(gamut, [1, 1, 1])
    cr = colorrgb(gamut, [1, 0, 0])
    cg = colorrgb(gamut, [0, 1, 0])
    cb = colorrgb(gamut, [0, 0, 1])
    cy = colorrgb(gamut, [1, 1, 0])
    cc = colorrgb(gamut, [0, 1, 1])
    cm = colorrgb(gamut, [1, 0, 1])

    # Interpolate two sides of a given face and interpolate the rest
    s1 = colorrgb.steps([cy, cw], steps=res, space=gamut)
    s2 = colorrgb.steps([cg, cc], steps=res, space=gamut)
    s3 = colorrgb.steps([cr, cm], steps=res, space=gamut)
    s4 = colorrgb.steps([ck, cb], steps=res, space=gamut)
    render_rect_face(fig, colorrgb, s1, s2, ('x', 'z'), space, gamut, res, opacity, edges, faces, ecolor, fcolor, gmap)
    render_rect_face(fig, colorrgb, s1, s3, ('y', 'z'), space, gamut, res, opacity, edges, faces, ecolor, fcolor, gmap)
    render_rect_face(fig, colorrgb, s3, s4, ('x', 'z'), space, gamut, res, opacity, edges, faces, ecolor, fcolor, gmap)
    render_rect_face(fig, colorrgb, s4, s2, ('y', 'z'), space, gamut, res, opacity, edges, faces, ecolor, fcolor, gmap)
    s1 = colorrgb.steps([cb, cc], steps=res, space=gamut)
    s2 = colorrgb.steps([cm, cw], steps=res, space=gamut)
    render_rect_face(fig, colorrgb, s1, s2, ('x', 'y'), space, gamut, res, opacity, edges, faces, ecolor, fcolor, gmap)
    s1 = colorrgb.steps([ck, cg], steps=res, space=gamut)
    s2 = colorrgb.steps([cr, cy], steps=res, space=gamut)
    render_rect_face(fig, colorrgb, s1, s2, ('x', 'y'), space, gamut, res, opacity, edges, faces, ecolor, fcolor, gmap)

    return fig


def plot_gamut_in_space(
    space,
    gamut,
    title="",
    dark=False,
    resolution=200,
    opacity=1.0,
    edges=False,
    faces=False,
    edge_color='#333333',
    face_color='',
    gmap=None,
    size=(800, 800),
    camera=None,
    aspect=None,
    projection='perspective'
):
    """Plot the given space in sRGB."""

    if gmap is None:
        gmap = {}

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
    is_regular = isinstance(target, Regular)
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

    edgecolor = Color(edge_color).convert('srgb').to_string(hex=True, fit=gmap) if edge_color else None

    target = Color.CS_MAP[space]
    if is_regular:
        # Use a rectangular space for RGB-ish spaces to give a sharper cube
        return render_space_rect(fig, space, gamut, resolution, opacity, edges, faces, edgecolor, face_color, gmap)
    else:
        # Render the space plot using a cylindrical space as the gamut space
        return render_space_cyl(fig, space, gamut, resolution, opacity, edges, faces, edgecolor, face_color, gmap)


def plot_gamut_frames(fig, space, gamut_wires, gmap):
    """Plot gamut wire frames."""

    if not gamut_wires:
        return

    wires = gamut_wires.split(';') if gamut_wires else []
    for wire in wires:
        gamut, color, res = wire.split(':')
        res = max(8, int(res))
        if res == 50:
            res = 51

        opacity = 0.2
        ecolor = None
        edges = False
        faces = False
        fcolor = ''
        if color.startswith('edge('):
            parts = [c.strip() for c in color[5:-1].split(',')]
            if len(parts) == 1:
                p1 = parts[0]
                p2 = '0.2'
            else:
                p1, p2 = parts
            if p1.lower() != 'false':
                edges = True
                if p1.lower() != 'true':
                    ecolor = Color(p1).convert('srgb').to_string(hex=True, fit=gmap)
            opacity = float(p2)

        target = Color.CS_MAP[space]
        is_regular = isinstance(target, Regular)
        if is_regular:
            # Use a rectangular space for RGB-ish spaces to give a sharper cube
            render_space_rect(fig, space, gamut, res, opacity, edges, faces, ecolor, fcolor, gmap)
        else:
            # Render the space plot using a cylindrical space as the gamut space
            render_space_cyl(fig, space, gamut, res, opacity, edges, faces, ecolor, fcolor, gmap)


def plot_colors(fig, space, gamut, gmap_colors, colors, gmap):
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

            fig.add_trace(
                go.Scatter3d(
                    x=x, y=y, z=z,
                    line={'color': 'black', 'width': 2},
                    marker={
                        'color': c2.convert('srgb').to_string(hex=True, fit=gmap),
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
    interp_space,
    interp_method,
    hue,
    carryfoward,
    powerless,
    extrapolate,
    steps,
    gmap,
    simulate_alpha
):
    """Plot interpolations."""

    if not interp_colors:
        return

    colors = Color.steps(
        interp_colors.split(';'),
        space=interp_space,
        steps=steps,
        hue=hue,
        carryfoward=carryfoward,
        powerless=powerless,
        extrapolate=extrapolate,
        method=interp_method
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
        store_coords(c, x, y, z, flags)

        c.convert('srgb', in_place=True)
        c.fit(**gmap)
        if simulate_alpha:
            cmap.append(Color.layer([c, 'white'], space='srgb').to_string(hex=True))
        else:
            cmap.append(c.to_string(comma=True, alpha=False))

    trace = go.Scatter3d(
        x=x, y=y, z=z,
        mode = 'markers',
        marker={'color': cmap, 'opacity': 1},
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
        default='srgb',
        help=(
            'Gamut space to render space in. Gamut space must be bounded and must have channels in the range [0, 1].'
            'As only a shell is rendered for the gamut, the target space should be less than or equal to the size of '
            'the target gamut or there will be areas that do not render. Cylindrical spaces based specifically off '
            'an RGB gamut, such as HSL being based on sRGB, will only be done under the related gamut and will ignore '
            'this option.'
        )
    )
    parser.add_argument(
        '--gamut-shell',
        default='',
        help=(
            'Gamut shells are specified in the form gamut:edge(bool | color, int):resolution. Each shell should be '
            'separated by a semicolon. The first parameter of the edge function can be `true` to turn on edges, '
            '`false` to turn off edges, or a color to set the edges to one color. The next parameter sets the opacity, '
            'of the surface (not the edges), the default being 0.2 if opacity is omitted.'
        )
    )
    parser.add_argument('--gmap', default='raytrace', help="Gamut mapping algorithm.")
    parser.add_argument('--gmap-colors', default='', help='Color(s) to gamut map, separated by semicolons.')
    parser.add_argument(
        '--gmap-options',
        default='{}',
        help='Options to pass to the gamut mapping method (JSON string).'
    )
    parser.add_argument(
        '--colors',
        default='',
        help='Plot arbitrary color points. Colors are separated with semicolons.'
    )

    # Interpolation visualization
    parser.add_argument('--interp-colors', default='', help='Interpolation colors separated by semicolons.')
    parser.add_argument('--interp-method', default='linear', help="Interplation method to use: linear, bezier, etc.")
    parser.add_argument('--interp-space', default='oklab', help="Interpolation space.")
    parser.add_argument(
        '--interp-alpha', action='store_true', help="Simulate interpolation opacity by overlaying on white"
    )
    parser.add_argument('--hue', default='shorter', help="Hue interpolation handling.")
    parser.add_argument('--extrapolate', action='store_true', help='Extrapolate values.')
    parser.add_argument('--powerless', action='store_true', help="Treat achromatic hues as powerless.")
    parser.add_argument('--carryfoward', action='store_true', help="Carry forward undefined channels.")
    parser.add_argument('--steps', type=int, default=100, help="Interpolation steps.")

    # Graphical and plotting options
    parser.add_argument('--title', '-t', default='', help="Provide a title for the diagram.")
    parser.add_argument('--opacity', default=1.0, type=float, help="opacity")
    parser.add_argument(
        '--resolution', '-r',
        default="200",
        help=(
            "How densely to render the figure. Some spaces need higher resolution to flesh out certain areas, "
            "but it comes at the cost of speed. Minimum is 60, default is 200."
        )
    )
    parser.add_argument('--edges', '-e', action="store_true", help="Plot edges.")
    parser.add_argument('--faces', '-f', action="store_true", help="Colorize faces for a low-res poly look.")
    parser.add_argument(
        '--edge-color',
        default="",
        help="Edge color. If no color is specified, edges will be based on vertices."
    )
    parser.add_argument(
        '--face-color',
        default="",
        help="Face color. If no color is specified, faces will be calculated as the average of the vertices."
    )
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

    aspect = {k: float(v) for k, v in zip(['x', 'y', 'z'], args.aspect_ratio.split(':'))}
    res = max(8, int(args.resolution))
    gmap = {'method': args.gmap}
    gmap.update(json.loads(args.gmap_options))

    # Plot the color space
    fig = plot_gamut_in_space(
        args.space,
        args.gamut,
        title=args.title,
        dark=args.dark,
        resolution=res,
        opacity=args.opacity,
        edges=args.edges,
        faces=args.faces,
        edge_color=args.edge_color,
        face_color=args.face_color,
        gmap=gmap,
        size=(args.width, args.height),
        camera={'a': args.azimuth, 'e': args.elevation, 'r': args.distance},
        aspect=aspect,
        projection=args.projection
    )

    # Plot additional gamut frames
    plot_gamut_frames(fig, args.space, args.gamut_shell, gmap)

    # Plot interpolation
    plot_interpolation(
        fig,
        args.space,
        args.interp_colors,
        args.interp_space,
        args.interp_method,
        args.hue,
        args.carryfoward,
        args.powerless,
        args.extrapolate,
        args.steps,
        gmap,
        args.interp_alpha
    )

    # Plot gamut mapping examples
    plot_colors(fig, args.space, args.gamut, args.gmap_colors, args.colors, gmap)

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
