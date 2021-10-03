"""Calculate range in sRGB."""
import sys
import argparse
import os
import itertools

sys.path.insert(0, os.getcwd())

from coloraide import Color  # noqa: E402
from coloraide import util  # noqa: E402
from coloraide.spaces import Lchish, Cylindrical  # noqa: E402


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='calc_range_srgb.py', description='Calculate srgb range in the given color.'
    )
    # Flag arguments
    parser.add_argument(
        '--color', '-c', action='store', default='', help="The color whose range relative to sRGB will be calculated."
    )
    parser.add_argument(
        '--rgb', '-r', action='store', default='srgb', help="The RGB space which the color will be sized against."
    )
    args = parser.parse_args()

    return run(args.color, args.rgb)


def convert(space, x, y, z, data):
    """Convert to the target space(s) and return the coordinates."""

    color = Color('color({} {} {} {})'.format(space, x / 255, y / 255, z / 255))
    print('\rCurrent: {}'.format(color.to_string(hex=True)), end="")
    for space in data.keys():
        color2 = color.convert(space)
        x, y, z = util.no_nan(color2.coords())

        data[space]["min_x"] = min(x, data[space]["min_x"])
        data[space]["min_y"] = min(y, data[space]["min_y"])
        data[space]["min_z"] = min(z, data[space]["min_z"])
        data[space]["max_x"] = max(x, data[space]["max_x"])
        data[space]["max_y"] = max(y, data[space]["max_y"])
        data[space]["max_z"] = max(z, data[space]["max_z"])


def run(target, rgb):
    """Run."""

    data = {}
    if target:
        data[target] = {
            "max_x": float('-inf'),
            "max_y": float('-inf'),
            "max_z": float('-inf'),
            "min_x": float('inf'),
            "min_y": float('inf'),
            "min_z": float('inf')
        }
    else:
        for space in Color.CS_MAP.keys():
            data[space] = {
                "max_x": float('-inf'),
                "max_y": float('-inf'),
                "max_z": float('-inf'),
                "min_x": float('inf'),
                "min_y": float('inf'),
                "min_z": float('inf')
            }

    # Setup hues as 0 - 360. Due to how we approach this,
    # some spaces will yield a value very close,
    # but we know this is a valid range.
    for k, v in data.items():
        space = Color.CS_MAP[k]
        if issubclass(space, Lchish):
            v['min_z'] = 0
            v['max_z'] = 360
        elif issubclass(space, Cylindrical):
            v['min_x'] = 0
            v['max_x'] = 360

    print('-> Current:', end="")
    # Calculate by taking the colors on the outer most edge of the RGB space.
    for c1, c2 in itertools.product(
        (x for x in range(0, 256)),
        (x for x in range(0, 256))
    ):

        convert(rgb, 0, c1, c2, data)
        convert(rgb, 255, c1, c2, data)

        convert(rgb, c1, 0, c2, data)
        convert(rgb, c1, 255, c2, data)

        convert(rgb, c1, c2, 0, data)
        convert(rgb, c1, c2, 255, data)

    for space in data.keys():
        print('')
        chan_x, chan_y, chan_z = Color('white').convert(space)._space.CHANNEL_NAMES[:-1]
        print('---- {} range in {} ----'.format(space, rgb))
        print('{}: [{}, {}]'.format(
            chan_x, util.round_half_up(data[space]["min_x"], 3), util.round_half_up(data[space]["max_x"], 3))
        )
        print('{}: [{}, {}]'.format(
            chan_y, util.round_half_up(data[space]["min_y"], 3), util.round_half_up(data[space]["max_y"], 3))
        )
        print('{}: [{}, {}]'.format(
            chan_z, util.round_half_up(data[space]["min_z"], 3), util.round_half_up(data[space]["max_z"], 3))
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
