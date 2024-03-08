"""Testing for ray tracing."""
import sys
import os
import plotly.graph_objects as go
import argparse

sys.path.insert(0, os.getcwd())

from coloraide.gamut.fit_raytrace import raytrace_box  # noqa: E402


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
        '--title', '-t', help="Title."
    )
    parser.add_argument('--height', '-H', type=int, default=800, help="Diagram height.")
    parser.add_argument('--width', '-W', type=int, default=800, help="Diagram width.")
    args = parser.parse_args()

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
    go.Figure(
        layout={
            'title': title,
            'width': args.width,
            'height': args.height
        },
        data=data
    ).show()
