"""Calculate range in sRGB."""
import sys
import argparse
import os

sys.path.insert(0, os.getcwd())

from coloraide import Color  # noqa: E402
from coloraide import util  # noqa: E402


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
    args = parser.parse_args()

    return run(args.color, args.rgb, args.res)


def run(target, rgb, res):
    """Run."""

    max_x = float('-inf')
    max_y = float('-inf')
    max_z = float('-inf')
    min_x = float('inf')
    min_y = float('inf')
    min_z = float('inf')

    print('-> Current:', end="")
    x = y = z = 0
    color = Color(rgb, [0, 0, 0])
    while True:
        color.update(rgb, [x / res, y / res, z / res])
        print('\rCurrent: {}'.format(color.to_string(color=True)), end="")
        cx, cy, cz = color.convert(target).coords()
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
    chan_x, chan_y, chan_z = Color('white').convert(target)._space.CHANNEL_NAMES
    print('---- {} range in {} ----'.format(target, rgb))
    print('{}: [{}, {}]'.format(chan_x, util.round_half_up(min_x, 3), util.round_half_up(max_x, 3)))
    print('{}: [{}, {}]'.format(chan_y, util.round_half_up(min_y, 3), util.round_half_up(max_y, 3)))
    print('{}: [{}, {}]'.format(chan_z, util.round_half_up(min_z, 3), util.round_half_up(max_z, 3)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
