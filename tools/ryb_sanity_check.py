"""Script to make sure conversion between RYB and sRGB meets the minimum accuracy."""
import sys
import argparse
import os

sys.path.insert(0, os.getcwd())

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


def run(space):
    """Run the check."""

    # Check the corners first, if they don't resolve, we will have issues elsewhere.
    print('---Corners---')
    for corner in RYB_CORNERS:
        ryb = Color(space, corner)
        srgb = ryb.convert('srgb')
        ryb2 = srgb.convert(space)
        str1, str2 = ryb.to_string(), ryb2.to_string()
        print(str1, str2)
        if str1 != str2:
            print('Colors do not match!')
            return 1

    # Iterate through the RYB space ensuring conversion works as expected
    count = 0
    for i in range(res):
        for j in range(res):
            for k in range(res):
                print('-----{}-----'.format(count))
                ryb = Color(space, [i / div, j / div, k / div])
                srgb = ryb.convert('srgb')
                ryb2 = srgb.convert(space)
                str1, str2 = ryb.to_string(), ryb2.to_string()
                print(str1, str2)
                if str1 != str2:
                    print('Colors do not match!')
                    return 1
                count += 1
    return 0


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='ryb_sanity_check.py', description='Ensure we have minimal accuracy for RYB conversion.'
    )
    # Flag arguments
    parser.add_argument(
        '--space', '-s', default='', help="RYB space against sRGB."
    )
    args = parser.parse_args()

    if args.space in SPACES:
        return run(args.space)

    print('Unrecongnized color space{}'.format(args.space))
    return 1


if __name__ == "__main__":
    sys.exit(main())
