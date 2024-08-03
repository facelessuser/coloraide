"""Calculate range in sRGB."""
import sys
import argparse
import os
import math

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide import algebra as alg  # noqa: E402


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='calc_range_srgb.py', description='Calculate RGB range in the given color.'
    )
    # Flag arguments
    parser.add_argument(
        '--color', '-c', action='store', default='', help="The color whose range relative to RGB will be calculated."
    )
    parser.add_argument(
        '--rgb', '-r', action='store', default='srgb', help="The RGB space which the color will be sized against."
    )
    parser.add_argument(
        '--res', '-s', type=int, default=100, help="Resolution to use when calculating range, default is 100."
    )
    parser.add_argument(
        '--precision', '-p', type=int, default=3, help="Precision for displaying the range."
    )
    args = parser.parse_args()

    return run(args.color, args.rgb, args.res, args.precision)


def run(target, rgb, res, p):
    """Run."""

    max_x = -math.inf
    max_y = -math.inf
    max_z = -math.inf
    min_x = math.inf
    min_y = math.inf
    min_z = math.inf

    print(' Current:', end="")
    template = '\r Current: {}'.ljust(30)
    x = y = z = 0
    color = Color(rgb, [0, 0, 0])
    while True:
        color.update(rgb, [x / res, y / res, z / res])
        print(template.format(color.to_string(color=True)), end="\r")
        cx, cy, cz = color.convert(target)[:-1]
        if cx < min_x:
            min_x = cx
        if cy < min_y:
            min_y = cy
        if cz < min_z:
            min_z = cz
        if cx > max_x:
            max_x = cx
        if cy > max_y:
            max_y = cy
        if cz > max_z:
            max_z = cz

        if x == y == z == res:
            break
        elif y == z == res:
            x += 1
            y = z = 0
        elif z == res:
            y += 1
            z = 0
        else:
            z += 1

    print('')
    chan_x, chan_y, chan_z = Color('white').convert(target)._space.CHANNELS
    print(f'---- {target} range in {rgb} ----')
    print(f'{chan_x}: [{alg.round_half_up(min_x, p)}, {alg.round_half_up(max_x, p)}]')
    print(f'{chan_y}: [{alg.round_half_up(min_y, p)}, {alg.round_half_up(max_y, p)}]')
    print(f'{chan_z}: [{alg.round_half_up(min_z, p)}, {alg.round_half_up(max_z, p)}]')

    return 0


if __name__ == "__main__":
    sys.exit(main())
