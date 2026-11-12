"""
Script to make sure conversion between RYB and sRGB meets the minimum accuracy.

Before round tripping colors, the RYB cube itself is checked as not every cube can be inverted reliably:

- The cube must not fold over on itself. If it does, different RYB colors can produce the exact same sRGB color, and
  no solver can tell them apart. This is a hard failure.
- The cube should not be singular, or nearly so. This does not prevent a round trip, but precision is lost near the
  singularity. This is only a warning.
"""
import sys
import argparse
import os

sys.path.insert(0, os.getcwd())

from coloraide import algebra as alg  # noqa: E402

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color

res = 50
div = 50 - 1

RYB_CORNERS = [
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [1.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
    [1.0, 0.0, 1.0],
    [0.0, 1.0, 1.0],
    [1.0, 1.0, 1.0]
]

SPACES = ('ryb', 'ryb-biased')

# Tolerance for treating a Bernstein coefficient as zero
ZERO = 1e-12
# If the determinant can get this close to zero, the cube is considered singular. Precision degrades smoothly as the
# determinant approaches zero: round trip error is roughly 1e-11 when it can reach 1e-7, and roughly 1e-8 when the
# cube is exactly singular (e.g. Gosset and Chen's orange sits exactly between red and yellow).
SINGULAR = 1e-6


def jacobian_det(cube, p):
    """
    Get the determinant of the Jacobian of the trilinear interpolation at `p`.

    The interpolation is linear along each axis, so each partial derivative is exactly the difference between the
    interpolation at the top and bottom of that axis.
    """

    cols = []
    for axis in range(3):
        hi = list(p)
        lo = list(p)
        hi[axis] = 1.0
        lo[axis] = 0.0
        cols.append([a - b for a, b in zip(alg.lerp3d(cube, hi), alg.lerp3d(cube, lo))])
    return alg.det([[cols[j][i] for j in range(3)] for i in range(3)])


def bernstein_coefficients(cube):
    """
    Get the Bernstein coefficients of the Jacobian determinant over the unit cube.

    Each column of the Jacobian is linear in the two other variables, so the determinant has degree 2 in each variable.
    That means it is exactly described by 3x3x3 coefficients, which we get by sampling at 0, 0.5, and 1 and converting
    each axis to the Bernstein basis. The determinant over the cube never leaves the range of these coefficients.
    """

    pts = (0.0, 0.5, 1.0)
    f = [[[jacobian_det(cube, (x, y, z)) for z in pts] for y in pts] for x in pts]

    def to_bernstein(v):
        return [v[0], 2 * v[1] - (v[0] + v[2]) / 2, v[2]]

    for i in range(3):
        for j in range(3):
            f[i][j] = to_bernstein(f[i][j])
    for i in range(3):
        for k in range(3):
            c = to_bernstein([f[i][j][k] for j in range(3)])
            for j in range(3):
                f[i][j][k] = c[j]
    for j in range(3):
        for k in range(3):
            c = to_bernstein([f[i][j][k] for i in range(3)])
            for i in range(3):
                f[i][j][k] = c[i]
    return [v for plane in f for row in plane for v in row]


def check_cube(cube):
    """
    Check that the RYB cube can be reliably inverted.

    Returns a non-zero value if the cube folds over on itself.
    """

    print('---Cube---')
    coeffs = bernstein_coefficients(cube)
    low, high = min(coeffs), max(coeffs)
    print(f'Jacobian determinant is bounded by [{low:+.6f}, {high:+.6f}]')

    # The sign of the determinant only tells us the orientation, but it must be the same everywhere. If it changes,
    # the interpolation folds over on itself, and distinct RYB colors will share the same sRGB color.
    if low < -ZERO and high > ZERO:
        print(
            'Cube folds over on itself!\n'
            'Different RYB colors map to the same sRGB color, so conversions cannot round trip. '
            'Look for a corner that is nearly on the line between two neighboring corners (e.g. orange between red '
            'and yellow) and move it to the other side of that line.'
        )
        return 1

    # The closest the determinant can get to zero. At zero the cube is singular and Newton's method converges slowly
    # and loses precision there, unless it starts very close to the answer.
    closest = low if low > ZERO else (-high if high < -ZERO else 0.0)
    if closest < SINGULAR:
        print(
            'WARNING: Cube is singular, or nearly so (the determinant can reach '
            f'{closest:.2e}). The cube does not fold, but expect reduced precision near the singularity.'
        )
    else:
        print('Cube does not fold and is not near singular.')
    return 0


def run(space):
    """Run the check."""

    # Check the corners first, if they don't resolve, we will have issues elsewhere.
    print('---Corners---')
    for corner in RYB_CORNERS:
        ryb = Color(space, corner)
        srgb = ryb.convert('srgb')
        ryb2 = srgb.convert(space)
        str1, str2 = ryb.serialize(), ryb2.serialize()
        print(str1, str2)
        if str1 != str2:
            print('Colors do not match!')
            return 1

    # Iterate through the RYB space ensuring conversion works as expected
    count = 0
    for i in range(res):
        for j in range(res):
            for k in range(res):
                print(f'-----{count}-----')
                ryb = Color(space, [i / div, j / div, k / div])
                srgb = ryb.convert('srgb')
                ryb2 = srgb.convert(space)
                str1, str2 = ryb.serialize(), ryb2.serialize()
                print(str1, str2)
                if str1 != str2:
                    print('Colors do not match!')
                    return 1
                count += 1
    return 0


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='ryb_sanity_check.py', description='Ensure we have sufficient accuracy for RYB conversion.'
    )
    # Flag arguments
    parser.add_argument(
        '--space', '-s', default='', help="RYB space against sRGB."
    )
    parser.add_argument(
        '--cube-only', '-c', action='store_true', help="Only check the cube's properties, skip the round trip check."
    )
    args = parser.parse_args()

    if args.space in SPACES:
        result = check_cube(Color.CS_MAP[args.space].RYB_CUBE)
        if result or args.cube_only:
            return result
        return run(args.space)

    print(f'Unrecongnized color space{args.space}')
    return 1


if __name__ == "__main__":
    sys.exit(main())
