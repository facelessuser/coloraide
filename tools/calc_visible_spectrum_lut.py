"""
Build up a LUT of the visible spectrum.

Construct the Rösch-MacAdam solid and reduce chroma within in the xyY
color space to approximate the gamut. Build up a LUT from this data.

The idea is based on  http://www.brucelindbloom.com/index.html?LabGamutDisplayHelp.html.

More specifically, this borrows from an approach by Colour Science's Colour library.
It uses the pulse width wave ordering and produces the entire Rösch-MacAdam solid.
"""
import sys
import os
from scipy.spatial import Delaunay
import textwrap

sys.path.insert(0, os.getcwd())

from coloraide.everything import ColorAll as Color
from coloraide import algebra as alg
from coloraide import cmfs
from coloraide import illuminants
from coloraide import cat

WHITE = cat.WHITES['2deg']['D65']


def create_rosch_macadam_solid():
    """Generate the Rösch-MacAdam solid."""

    start = 360
    end = 780
    steps = 5

    # Generate pulse wave
    wavelengths = list(range(start, end + 1, steps))
    l = len(wavelengths)
    square_waves_basis = [[1.0 if e1 < e2 else 0 for e1 in range(l)] for e2 in range(1, l)]

    square_waves = []
    for i in range(l):
        for j, sw in enumerate(square_waves_basis):
            square_waves.append(alg.roll(sw, i - j // 2))

    # Filter out jagged pulses
    square_waves = square_waves[::2]

    pulse_waves = alg.vstack(
        [
            alg.zeros(l),
            alg.vstack(square_waves),
            alg.ones(l),
        ]
    )

    # Calculate XYZ values via Integration
    xyz_bar = [[], [], []]
    for i in range(start, end + 1, steps):
        xyz_bar[0].append(cmfs.CIE_1931_2DEG[i][0])
        xyz_bar[1].append(cmfs.CIE_1931_2DEG[i][1])
        xyz_bar[2].append(cmfs.CIE_1931_2DEG[i][2])
    illuminant = [illuminants.D65[r] for r in range(start, end + 1, steps)]

    xyz = alg.matmul(xyz_bar, alg.diag(illuminant))
    xyz = alg.transpose(alg.divide(xyz, alg.vdot(xyz_bar[1], illuminant)))

    return alg.dot(pulse_waves, xyz)


def in_gamut(tri, color):
    """Check if Lab color is within the visible spectrum."""

    return tri.find_simplex(color.convert('xyz-d65')[:-1], tol=1e-12) >= 0


def build_lut(location):
    """Build the LUT for the Rösch-MacAdam solid."""

    # Create the solid
    tri = Delaunay(create_rosch_macadam_solid())

    # Loop from 0 - 100 luminance and 0 -360 hue at some number of step.
    # We iterate in luminance and convert to Lab lightness for more linear steps.
    table = []
    hues = alg.linspace(0, 360, 361)
    # 0 needs to be included, but it gives us nothing as far as the shape is concerned,
    # 1e-10 will give us something close to the largest base size.
    luminance = [0, 1e-10, *[i / 100 for i in alg.linspace(1, 100, 20)]]
    for Y in luminance:
        best = 0
        row = []
        # Iterate enough hues to get a decent shape within the visible spectrum.
        # This won't give us a perfect curve, but good enough to be roughly within the gamut.
        for h in hues:
            # Setup CIE Lab in D65 with enough chroma to require reduction at all lightness and hue we are sampling
            low = 0
            high = 10

            x, y = alg.add(alg.polar_to_rect(high, h), WHITE)
            mapcolor = Color('xyy', [x, y, Y])

            # Adjust the bounds based on whether we are in gamut or not, but bail when high and low
            # essentially converge.
            count = 0
            while (high - low) > 1e-12:
                value = (high + low) * 0.5
                mapcolor[0:2] = alg.add(alg.polar_to_rect(value, h), WHITE)

                if in_gamut(tri, mapcolor):
                    low = alg.rect_to_polar(*alg.subtract(mapcolor[:2], WHITE))[0]
                else:
                    high = alg.rect_to_polar(*alg.subtract(mapcolor[:2], WHITE))[0]
                    best = high
                count += 1

            row.append(best)
            print(f'==> Luminance: {Y} Hue: {h} Chroma: {best}')

        table.append(row)

    table = alg.transpose(table)

    with open(location, 'w', encoding='utf-8') as f:
        f.write(
            textwrap.dedent(
                f'''
                """
                LUT for the Rösch-MacAdam solid.

                Values of xyY stored in a polar form derived from xy pairs.

                Luminance --> 0 - 1
                Hues 0 - 360
                  |  ...
                  V  ...

                LUT is created by building a 3D mesh of the Rösch-MacAdam solid
                and creating colors at a given luminance at varying degrees around
                the outside the solid. Colors are tested to see if they are within
                the solid, and if not, bisection is used to reduce the distance until
                we are close to the surface.
                """
                LUMINANCE = {alg.pretty(luminance)}
                HUE = {alg.pretty(hues)}
                '''
            ).strip()
        )
        f.write('\n\nLUT = ' + alg.pretty(table))


if __name__ == "__main__":
    sys.exit(build_lut('coloraide/gamut/rosch_macadam_solid.py'))
