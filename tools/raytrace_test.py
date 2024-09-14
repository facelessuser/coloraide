"""Testing for ray tracing."""
import sys
import os
import plotly.graph_objects as go
import plotly.io as io
import argparse
import json

sys.path.insert(0, os.getcwd())

import tools.gamut_3d_plotly as plt3d  # noqa: E402
from coloraide.gamut.fit_raytrace import raytrace_box, project_onto  # noqa: E402
from coloraide.gamut.tools import adaptive_hue_independent  # noqa: E402
from coloraide.gamut import fit_raytrace as fit  # noqa: E402
from coloraide.everything import ColorAll as Color  # noqa: E402
from coloraide import algebra as alg  # noqa: E402
from coloraide.spaces.lch import LCh  # noqa: E402


class _LCh(LCh):
    """Custom LCh."""

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


def coerce_to_lch(space):
    """Coerce Lab to LCh."""

    cs = Color.CS_MAP[space]
    name = cs.NAME

    class CustomLCh(_LCh):
        NAME = '-cylinder'
        SERIALIZE = ('-cylinder',)
        BASE = name
        WHITE = cs.WHITE
        DYAMIC_RANGE = cs.DYNAMIC_RANGE
        INDEXES = cs.indexes()
        ORIG_SPACE = cs

        def is_achromatic(self, coords) -> bool | None:
            """Check if space is achromatic."""

            return self.ORIG_SPACE.is_achromatic(self.to_base(coords))

    class ColorCyl(Color):
        """Custom color."""

    ColorCyl.register(CustomLCh())

    return ColorCyl


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
    opacity=1
):
    """Plot interpolations, but force Lab to operate like LCh."""

    if not interp_colors:
        return

    if not Color.CS_MAP[interp_space].is_polar():
        Color_ = coerce_to_lch(interp_space)
        interp_space = '-cylinder'
    else:
        Color_ = Color

    colors = Color_.steps(
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
        'is_labish': isinstance(target, plt3d.Labish),
        'is_lchish': isinstance(target, plt3d.LChish),
        'is_hslish': isinstance(target, plt3d.HSLish),
        'is_hwbish': isinstance(target, plt3d.HWBish),
        'is_hsvish': isinstance(target, plt3d.HSVish)
    }

    x = []
    y = []
    z = []
    cmap = []
    for c in colors:
        c.convert(space, in_place=True)
        plt3d.store_coords(c, x, y, z, flags)

        c.convert('srgb', in_place=True)
        c.fit(**gmap)
        cmap.append(c.to_string(hex=True))

    trace = go.Scatter3d(
        x=x, y=y, z=z,
        mode = 'markers',
        marker={'color': cmap},
        showlegend=False
    )

    trace.update(opacity=opacity)
    fig.add_trace(trace)


def raytrace(args):
    """Test ray tracing directly."""

    # Cast rays and find intersection with the defined box.
    data = []
    bmin = [float(v) for v in args.bmin.strip()[1:-1].split(',')]
    bmax = [float(v) for v in args.bmax.strip()[1:-1].split(',')]

    for ray in args.ray:
        start, end = ([float(v.strip()) for v in c.split(',')] for c in [r.strip()[1:-1] for r in ray.split('->')])
        intersect = raytrace_box(start, end, bmin=bmin, bmax=bmax)
        px, py, pz = zip(start, end) if not intersect else zip(start, intersect, end)
        data.append(
            go.Scatter3d(
                x=px,
                y=py,
                z=pz,
                marker={"color": 'red' if not intersect else 'green', "size": 4}
            )
        )

    # Render box.
    xmin, ymin, zmin = bmin
    xmax, ymax, zmax = bmax
    data.append(
        go.Mesh3d(
            # 8 vertices of a cube
            x=[xmin, xmin, xmax, xmax, xmin, xmin, xmax, xmax],
            y=[ymin, ymax, ymax, ymin, ymin, ymax, ymax, ymin],
            z=[zmin, zmin, zmin, zmin, zmax, zmax, zmax, zmax],
            i=[7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 2],
            opacity=0.3,
            color='#eeddff',
            flatshading = True
        )
    )
    data[-1].update(hoverinfo='skip')

    title = args.title if args.title else ''
    return go.Figure(
        layout={
            'title': title,
            'width': args.width,
            'height': args.height
        },
        data=data
    )


def simulate_raytrace_gamut_mapping(args):
    """Simulate gamut mapping with ray tracing."""

    points = []
    color = Color(args.gamut_color)

    options = json.loads(args.gmap_options)
    pspace = options.get('pspace', 'lch-d65')
    adaptive = options.get('adaptive', 0.0)

    polar = color.CS_MAP[pspace].is_polar()
    space = args.gamut_rgb

    cs = color.CS_MAP[space]
    bmax = [1.0, 1.0, 1.0]

    # Requires an RGB-ish space, preferably a linear space.
    # Coerce RGB cylinders with no defined RGB space to RGB
    coerced = None
    if not isinstance(cs, fit.RGBish):
        coerced = color
        Color_, space = fit.coerce_to_rgb(type(color), cs)
        cs = Color_.CS_MAP[space]
        color = Color_(color)

    # If there is a non-linear version of the RGB space, results will be
    # better if we use that. If the target RGB space is HDR, we need to
    # calculate the bounding box size based on the HDR limit.
    sdr = cs.DYNAMIC_RANGE != 'hdr'
    linear = cs.linear()  # type: ignore[attr-defined]
    if linear and linear in color.CS_MAP:
        if not sdr:
            bmax = color.new(space, [chan.high for chan in cs.CHANNELS]).convert(linear)[:-1]
        space = linear

    orig = color.space()
    mapcolor = color.convert(pspace, norm=False) if orig != pspace else color.clone().normalize(nans=False)
    achroma = mapcolor.clone()
    first = mapcolor.clone()
    if polar:
        l, c, h = mapcolor._space.indexes()  # type: ignore[attr-defined]
        light = mapcolor[l]
        chroma = mapcolor[c]
        hue = mapcolor[h]
        ab = alg.polar_to_rect(chroma, hue)
        achroma[c] = 0
    else:
        l, a, b = mapcolor._space.indexes()  # type: ignore[attr-defined]
        ab = [mapcolor[a], mapcolor[b]]
        light = mapcolor[l]
        chroma, hue = alg.rect_to_polar(*ab)
        achroma[a] = 0
        achroma[b] = 0

    if adaptive:
        max_light = color.new(space, [1.0, 1.0, 1.0]).convert(pspace)[l]
        alight = adaptive_hue_independent(light / max_light, max(chroma, 0) / max_light, adaptive) * max_light
        achroma[l] = alight
    else:
        alight = light

    achromatic = [sum(achroma.clone().convert(space, in_place=True)[:-1]) / 3] * 3

    # Return white or black if the achromatic version is not within the RGB cube.
    bmx = bmax[0]
    point = achromatic[0]
    if point >= bmx:
        color.update(space, bmax, mapcolor[-1])
        points.append(first.convert(space)[:-1])
        points.append(color.convert(space)[:-1])
        points.append(achromatic)
    elif point <= 0:
        color.update(space, [0.0, 0.0, 0.0], mapcolor[-1])
        points.append(first.convert(space)[:-1])
        points.append(color.convert(space)[:-1])
        points.append(achromatic)
    else:
        print('Initial:', mapcolor)
        print('Anchor:', achroma.convert(pspace), '\n----')
        gamutcolor = mapcolor.convert(space)

        # Threshold for anchor adjustment
        low = 1e-6
        high = bmx - low

        # Create a ray from our current color to the color with zero chroma.
        # Trace the line to the RGB cube finding the intersection.
        # In between iterations, correct the L and H and then cast a ray
        # through the new corrected color finding the intersection again.
        for i in range(4):
            if i:
                gamutcolor.convert(pspace, in_place=True, norm=False)
                print('Uncorrected:', gamutcolor)

                if adaptive:
                    # Correct the point onto the desired interpolation path
                    if polar:
                        gamutcolor[l], a_, b_ = project_onto(
                            [gamutcolor[l], *alg.polar_to_rect(gamutcolor[c], gamutcolor[h])],
                            [light, *ab],
                            [alight, 0.0, 0.0]
                        )
                        gamutcolor[c], gamutcolor[h] = alg.rect_to_polar(a_,b_)
                    else:
                        gamutcolor[l], gamutcolor[a], gamutcolor[b] = project_onto(
                            [gamutcolor[l], gamutcolor[a], gamutcolor[b]],
                            [light, *ab],
                            [alight, 0.0, 0.0]
                        )

                else:
                    # Correct lightness and hue
                    gamutcolor[l] = alight
                    if polar:
                        gamutcolor[h] = hue
                    else:
                        gamutcolor[a], gamutcolor[b] = alg.polar_to_rect(
                            alg.rect_to_polar(gamutcolor[a], gamutcolor[b])[0],
                            hue
                        )

                print('Corrected:', gamutcolor)
                gamutcolor.convert(space, in_place=True)
                print('Corrected RGB:', gamutcolor, '\n----')

            coords = gamutcolor[:-1]
            intersection = raytrace_box(achromatic, coords, bmax=bmax)

            if i and all(low < x < high for x in coords):
                achromatic = coords

            if intersection:
                points.append(gamutcolor[:-1])
                points.append(intersection)
                points.append(achromatic)
                gamutcolor[:-1] = intersection
                continue
            break  # pragma: no cover

        print('Final:', gamutcolor.convert(pspace, norm=False))
        color.update(space, [alg.clamp(x, 0.0, bmx) for x in gamutcolor[:-1]])
        print('Clipped RGB:', color.convert(space))

    # If we have coerced a space to RGB, update the original
    if coerced:
        coerced.update(color)

    x, y, z = zip(*points)
    data = []
    i = 0
    while i < len(x):
        data.append(
            go.Scatter3d(
                x=x[i:i + 3],
                y=y[i:i + 3],
                z=z[i:i + 3],
                marker={"color": 'black', "size": 2},
                showlegend=False
            )
        )
        i += 3

    gmap = {'method': 'raytrace'}
    gmap.update(options)

    # Plot the color space
    fig = plt3d.plot_gamut_in_space(
        space,
        args.gamut_rgb,
        title=args.title,
        resolution=100,
        opacity=0.3,
        edges=False,
        gmap=gmap,
        size=(args.width, args.height)
    )

    fig.add_traces(data)

    if args.gamut_interp:
        plot_interpolation(
            fig,
            space,
            first.to_string(fit=False) + ';' + achroma.to_string(fit=False),
            pspace,
            'linear',
            'shorter',
            False,
            False,
            False,
            100,
            gmap,
            opacity=0.3
        )

    return fig


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog='raytrace_test.py', description='Test ray tracing.'
    )
    # Flag arguments
    parser.add_argument(
        '--bmax',
        '-B',
        default='(1,1,1)',
        help="Max axis aligned box point in the form `(x, y, z)`, default is (1, 1, 1)."
    )
    parser.add_argument(
        '--bmin',
        '-b',
        default='(0,0,0)',
        help="Min axis aligned box point in the form `(x, y, z)`, default is (0, 0, 0)."
    )
    parser.add_argument(
        '--ray', '-r', action='append', help="Ray described in the form (x1,y1,z1)->(x2,y2,z2)."
    )
    parser.add_argument(
        '--gamut-rgb', default='srgb', help="RGB space to gamut map within."
    )
    parser.add_argument(
        '--gamut-color', help="Color to gamut map."
    )
    parser.add_argument(
        '--gamut-interp', action='store_true', help="Show interpolation of color along constant lightness and hue."
    )
    parser.add_argument(
        '--gmap-options',
        default='{}',
        help='Options to pass to the gamut mapping method (JSON string).'
    )
    parser.add_argument(
        '--title', '-t', help="Title."
    )
    parser.add_argument('--height', '-H', type=int, default=800, help="Diagram height.")
    parser.add_argument('--width', '-W', type=int, default=800, help="Diagram width.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    args = parser.parse_args()

    if args.gamut_color:
        fig = simulate_raytrace_gamut_mapping(args)
    else:
        fig = raytrace(args)


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
