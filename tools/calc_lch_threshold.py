"""
Calculate the LCh threshold of LCh-ish colors.

Particularly, we are interested in seeing the greatest
chroma deviation from zero for achromatic colors.

We simply will take a number of RGB color spaces and loop
through all achromatic colors, significantly past white
to see how far from zero chroma deviates.

This is mainly due to the fact that many of these LCh-ish
color spaces, as they get close to zero, whether due to
the algorithm, the precision, floating point math, or
whatever the reason, the conversion to an achromatic color
in the LCh-ish space often is very, very close to zero, but
not quite.

The threshold is essentially used during conversion to round
off chroma if it is very, very close to zero giving better,
expected conversions.

Looking at its Lab counterpart's `a` and `b` value is optional.
This is mainly if you are curious to see how the other channels
respond, or if you wanted use `a` and `b` to determine achromatic
response.
"""
import sys
import argparse
import os
import re

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color

RE_LEAD_ZERO = re.compile(r'^0\.0+')


def run(lch, lab, verify):
    """Run the calculation."""

    max_chroma = 0.0
    max_a = 0.0
    max_b = 0.0

    for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
        max_chroma = 0.0
        max_a = 0.0
        max_b = 0.0

        for x in range(5000):
            # Create an achromatic RGB color
            color = Color(space, [x / 1000] * 3)
            if lab:
                labish = color.convert(lab)
                a_name, b_name = labish._space.labish_names()[1:]
                a = labish.get(a_name)
                b = labish.get(b_name)
                if abs(a) > max_a:
                    max_a = abs(a)
                if abs(b) > max_b:
                    max_b = abs(b)

            if lch:
                lchish = color.convert(lch)
                c_name = lchish._space.lchish_names()[1]
                chroma = lchish.get(c_name)
                if verify:
                    assert lchish.is_nan('hue'), str(lchish) + " <-> " + str(color)
                if chroma > max_chroma:
                    max_chroma = chroma

    if lab:
        print('{}: maximum a: {:.53f}'.format(lab, max_a))
        print('{}: maximum b: {:.53f}'.format(lab, max_b))

    if lch:
        num = '{:.53f}'.format(max_chroma)
        m = RE_LEAD_ZERO.match(num)
        minimum = '0'
        better = '0'
        if m and len(m.group(0)) != len(num):
            count = len(m.group(0)[2:])
            if int(num[m.end(0)]) == 9:
                # Close to rolling over
                minimum = '> 0.{}1'.format('0' * (count - 1))
            else:
                # Less than a decimal point of room
                minimum = '> 0.{}{}'.format('0' * count, str(int(num[m.end(0)]) + 1))
            # Give at least a little over a decimal point
            better = '> 0.{}2'.format('0' * (count - 1))
            print('{}: minimum threshold: {}'.format(lch, minimum))
            print('{}: relaxed threshold: {}'.format(lch, better))
        else:
            print('{}: minimum threshold: {}'.format(lch, '?'))
            print('{}: relaxed threshold: {}'.format(lch, '?'))

        print('{}: maximum chroma: {:.53f}'.format(lch, max_chroma))

        print(
            '\n* Only potential recommendations, adjustments can be made if desired.'
            '\n  If consraints are very tight, the minimum is probably best while the'
            '\n  relaxed would give a little more room assuming achromatic colors even'
            '\n  further out did not roll the next decimal point by one.'
        )

    return 0


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='calc_lch_threshold.py', description='Calculate achromatic threshold for LCh-ish colors.'
    )
    # Flag arguments
    parser.add_argument(
        '--lch', '-c', action='store', default='',
        help="The LCh color whose 'chroma' values you'd like to evaluate."
    )
    parser.add_argument(
        '--lab', '-l', action='store', default='',
        help="Optionally view Lab color whose 'ab' values you'd like evaluate."
    )
    parser.add_argument(
        '--verify', '-v', action='store_true',
        help='Verify the space has all values equated to an achromatic hue (NaN).'
    )
    args = parser.parse_args()

    if not args.lch and not args.lab:
        print('No spaces provided to test!')

    return run(args.lch, args.lab, args.verify)


if __name__ == "__main__":
    sys.exit(main())
