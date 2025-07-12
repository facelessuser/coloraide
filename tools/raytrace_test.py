"""Testing for ray tracing."""
import sys
import os
import plotly.graph_objects as go
import plotly.io as io
import argparse
import json

sys.path.insert(0, os.getcwd())

import tools.gamut_3d_plotly as plt3d  # noqa: E402
from coloraide.gamut import fit_raytrace as fit  # noqa: E402
from coloraide.everything import ColorAll as Color  # noqa: E402
from coloraide import algebra as alg  # noqa: E402


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
        intersect = fit.raytrace_box(start, end, bmin=bmin, bmax=bmax)
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

    gmap = json.loads(args.gmap)
    gmap['method'] = 'raytrace'

    pspace = gmap.get('pspace', 'oklch')
    adaptive = gmap.get('adaptive', 0.0)

    space = args.gamut_rgb

    cs = color.CS_MAP[space]

    coerced = False
    if not isinstance(cs, fit.Prism) or isinstance(cs, fit.Luminant):
        coerced = True
        cs = fit.coerce_to_rgb(cs)

    bmax = [chan.high for chan in cs.CHANNELS]

    linear = cs.linear()
    if linear and linear in color.CS_MAP:
        subtractive = cs.SUBTRACTIVE
        cs = color.CS_MAP[linear]
        if subtractive != cs.SUBTRACTIVE:
            bmax = color.new(space, [chan.low for chan in cs.CHANNELS]).convert(linear, in_place=True)[:-1]
        else:
            bmax = color.new(space, bmax).convert(linear, in_place=True)[:-1]
        space = linear
    print('Target RGB Space:', space)

    bmin = [chan.low for chan in cs.CHANNELS]

    orig = color.space()
    mapcolor = color.convert(pspace, norm=False) if orig != pspace else color.clone().normalize(nans=False)
    polar = color.CS_MAP[pspace].is_polar()
    achroma = mapcolor.clone()
    first = mapcolor.clone()

    if polar:
        l, c, h = mapcolor._space.indexes()
        achroma[c] = 0.0
    else:
        l, a, b = mapcolor._space.indexes()
        achroma[a] = 0.0
        achroma[b] = 0.0

    if adaptive:
        max_light = color.new('xyz-d65', fit.WHITE).convert(pspace, in_place=True)[l]
        alight = fit.adaptive_hue_independent(
            mapcolor[l] / max_light,
            max(mapcolor[c] if polar else alg.rect_to_polar(mapcolor[a], mapcolor[b])[0], 0) / max_light,
            adaptive
        ) * max_light
        achroma[l] = alight
    else:
        alight = mapcolor[l]

    anchor = cs.from_base(achroma.convert(space)[:-1]) if coerced else achroma.convert(space)[:-1]
    anchor = fit.project_onto(anchor, bmax, bmin)

    if anchor == bmax:
        color.update(space, cs.to_base(bmax) if coerced else bmax, mapcolor[-1])
        points.append(first.convert(space)[:-1])
        points.append(color.convert(space)[:-1])
        points.append(anchor)
    elif anchor == bmin:
        color.update(space, cs.to_base(bmin) if coerced else bmin, mapcolor[-1])
        points.append(first.convert(space)[:-1])
        points.append(color.convert(space)[:-1])
        points.append(anchor)
    else:
        print('Initial:', mapcolor)
        print('Anchor:', achroma.convert(pspace), '\n----')

        if polar:
            start = mapcolor[:-1]
            end = achroma[:-1]
        else:
            start = fit.to_polar(mapcolor[:-1], a, b)
            end = fit.to_polar(achroma[:-1], a, b)
            end[b] = start[b]

        last = None
        offset = 1e-15
        mapcolor.convert(space, in_place=True)
        for i in range(4):
            if i:
                mapcolor.convert(pspace, in_place=True, norm=False)
                print('Uncorrected:', mapcolor)

                coords = mapcolor[:-1]
                if adaptive:
                    if polar:
                        mapcolor[:-1] = fit.project_onto(coords, start, end)
                    else:
                        mapcolor[:-1] = fit.to_rect(fit.project_onto(fit.to_polar(coords, a, b), start, end), a, b)

                else:
                    coords[l] = start[l]
                    if polar:
                        coords[h] = start[h]
                    else:
                        fit.to_polar(coords, a, b)
                        coords[b] = start[b]
                        fit.to_rect(coords, a, b)
                    mapcolor[:-1] = coords

                print('Corrected:', mapcolor)
                mapcolor.convert(space, in_place=True)
                print('Corrected RGB:', mapcolor, '\n----')

            coords = cs.from_base(mapcolor[:-1]) if coerced else mapcolor[:-1]
            print('-->', anchor, coords)
            intersection = fit.raytrace_box(anchor, coords, bmin=bmin, bmax=bmax)
            print('===', intersection)
            if i and all((bmin[r] + offset) <= coords[r] <= (bmax[r] - offset) for r in range(3)):
                anchor = coords

            if intersection:
                points.append(mapcolor[:-1])
                points.append(intersection)
                points.append(anchor)
                last = cs.to_base(intersection) if coerced else intersection
                mapcolor[:-1] = last
                continue

            if last is not None:
                mapcolor[:-1] = last

            break

        print('Final:', mapcolor.convert(pspace, norm=False))
        if coerced:
            color.update(
                space,
                cs.to_base([alg.clamp(x, bmin[e], bmax[e]) for e, x in enumerate(cs.from_base(mapcolor[:-1]))]),
                mapcolor[-1]
            )
        else:
            color.update(space, [alg.clamp(x, bmin[e], bmax[e]) for e, x in enumerate(mapcolor[:-1])], mapcolor[-1])
        print('Clipped RGB:', color.convert(space))

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

    # Plot the color space
    fig = plt3d.plot_gamut_in_space(
        space,
        {args.gamut_rgb: {'opacity': 0.2, 'resolution': 100}},
        title=args.title,
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
        '--gmap',
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
                    f.write(fig.to_image(format=filetype, width=args.width, height=args.height))
        else:
            fig.show('browser')
