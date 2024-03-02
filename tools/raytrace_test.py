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
        '--size', '-S', default='1,1,1', help="Dimension sizes, default is 1:1:1."
    )
    parser.add_argument(
        '--start', '-s', help="Staring point of ray in the form x,y,z."
    )
    parser.add_argument(
        '--end', '-e', help="Ending point of ray in the form x,y,z."
    )
    args = parser.parse_args()

    origin = (0,0,0)
    size = [float(x) for x in args.size.split(',')]
    start = [float(x) for x in args.start.split(',')]
    end = [float(x) for x in args.end.split(',')]
    xmin, ymin, zmin = origin
    xmax, ymax, zmax = size

    face, pt = raytrace_box(size, start, end)
    px, py, pz = zip(start, end) if not pt else zip(start, pt, end)

    fig = go.Figure(data=[
        go.Scatter3d(
            x=px,
            y=py,
            z=pz,
            marker={"color": "red", "size": 4}
        ),
        go.Mesh3d(
            # 8 vertices of a cube
            x=[xmin, xmin, xmax, xmax, xmin, xmin, xmax, xmax],
            y=[ymin, ymax, ymax, ymin, ymin, ymax, ymax, ymin],
            z=[zmin, zmin, zmin, zmin, zmax, zmax, zmax, zmax],
            i=[7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 2],
            opacity=0.6,
            color='#bbbbff',
            flatshading = True
        )
    ])

    fig.show()
