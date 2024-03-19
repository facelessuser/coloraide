"""Testing for ray tracing."""
import sys
import os
import plotly.graph_objects as go
import argparse
import json

sys.path.insert(0, os.getcwd())

import tools.gamut_3d_plotly as plt3d  # noqa: E402
from coloraide.gamut.fit_raytrace import raytrace_box  # noqa: E402
from coloraide.gamut import fit_raytrace as fit  # noqa: E402
from coloraide.everything import ColorAll as Color  # noqa: E402
from coloraide import algebra as alg  # noqa: E402


def raytrace(args):
    """Test ray tracing directly."""

    # Cast rays and find intersection with the defined box.
    data = []
    bmin = [float(v) for v in args.bmin.strip()[1:-1].split(',')]
    bmax = [float(v) for v in args.bmax.strip()[1:-1].split(',')]

    for ray in args.ray:
        start, end = [[float(v.strip()) for v in c.split(',')] for c in [r.strip()[1:-1] for r in ray.split('->')]]
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

    lch = args.gamut_lch
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
    mapcolor = color.convert(lch, norm=False) if orig != lch else color.clone().normalize(nans=False)
    first = mapcolor.clone()
    l, c, h = mapcolor._space.indexes()  # type: ignore[attr-defined]
    mapcolor[c] = 0
    achroma = mapcolor.clone().convert(space, in_place=True)[:-1]

    # Return white or black if the achromatic version is not within the RGB cube.
    mn, mx = alg.minmax(achroma)
    bmx = bmax[0]
    if mx >= bmx:
        color.update(space, bmax, mapcolor[-1])
        points.append(first.convert(space)[:-1])
        points.append(color.convert(space)[:-1])
        points.append(achroma)
    elif mn <= 0:
        color.update(space, [0.0, 0.0, 0.0], mapcolor[-1])
        points.append(first.convert(space)[:-1])
        points.append(color.convert(space)[:-1])
        points.append(achroma)
    else:
        # gamutcolor = color.convert(space, norm=False) if orig != space else color.clone().normalize(nans=False)
        light = mapcolor[l]
        hue = mapcolor[h]
        mapcolor[c] = 1e-8
        gamutcolor = mapcolor.convert(space)

        # Create a ray from our current color to the color with zero chroma.
        # Trace the line to the RGB cube finding the intersection.
        # In between iterations, correct the L and H and then cast a ray
        # through the new corrected color finding the intersection again.
        for i in range(3):
            if i:
                gamutcolor.convert(lch, in_place=True)
                gamutcolor[l] = light
                gamutcolor[h] = hue
                gamutcolor.convert(space, in_place=True)
            intersection = raytrace_box(achroma, gamutcolor[:-1], bmax=bmax)
            if intersection:
                points.append(gamutcolor[:-1])
                points.append(intersection)
                points.append(achroma)
                gamutcolor[:-1] = intersection
                continue
            break  # pragma: no cover

        color.update(space, [alg.clamp(x, 0.0, bmx) for x in gamutcolor[:-1]])

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
    gmap.update(json.loads(args.gmap_options))

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
        plt3d.plot_interpolation(
            fig,
            space,
            first.to_string(fit=False) + ';' + mapcolor.to_string(fit=False),
            lch,
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
        '--gamut-lch', default='oklch', help="Perceptual space to simulate gamut mapping in."
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
    args = parser.parse_args()

    if args.gamut_color:
        fig = simulate_raytrace_gamut_mapping(args)
    else:
        fig = raytrace(args)

    fig.show()
