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
        '--size', '-s', default='1,1,1', help="Dimension sizes, default is 1:1:1."
    )
    parser.add_argument(
        '--ray', '-r', help="Staring point of ray in the form x1,y1,z1:x2,y2,z2;..."
    )
    parser.add_argument(
        '--title', '-t', help="Title."
    )
    parser.add_argument('--height', '-H', type=int, default=800, help="Height")
    parser.add_argument('--width', '-W', type=int, default=800, help="Width")
    args = parser.parse_args()

    data = []
    for ray in args.ray.split(';'):
        a, b = ray.split(':')
        origin = (0,0,0)
        size = [float(x) for x in args.size.split(',')]
        start = [float(x) for x in a.split(',')]
        end = [float(x) for x in b.split(',')]
        xmin, ymin, zmin = origin
        xmax, ymax, zmax = size

        face, pt = raytrace_box(size, start, end)
        px, py, pz = zip(start, end) if not pt else zip(start, pt, end)
        data.append(
            go.Scatter3d(
                x=px,
                y=py,
                z=pz,
                marker={"color": 'red' if not pt else 'green', "size": 4}
            )
        )

    data.append(
        go.Mesh3d(
            # 8 vertices of a cube
            x=[xmin, xmin, xmax, xmax, xmin, xmin, xmax, xmax],
            y=[ymin, ymax, ymax, ymin, ymin, ymax, ymax, ymin],
            z=[zmin, zmin, zmin, zmin, zmax, zmax, zmax, zmax],
            i=[7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 2],
            opacity=0.6,
            color='#ddddff',
            flatshading = True
        )
    )

    title = args.title if args.title else ''
    go.Figure(
        layout={
            'title': title,
            'width': args.width,
            'height': args.height
        },
        data=data
    ).show()
