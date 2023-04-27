"""Get the average color of an image."""
from functools import lru_cache
from PIL import Image
import time
import argparse
import sys
import os

# We want to load ColorAide from the working directory to pick up the version under development
sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color


def printt(t):
    """Print time."""

    print('Completed in: ', end='')
    s = t // 1e+9
    m = t // 1e+6
    u = t // 1000
    if s:
        s = t / 1e+9
        h = m = 0
        m = s // 60
        if m:
            s -= m * 60
            h = m // 60
            if h:
                m -= h * 60
        if h:
            print('{} hours '.format(h), end='')
        if m:
            print('{} minutes '.format(m), end='')
        print('{} sec'.format(s))
    elif m:
        print('{} msec'.format(t / 1e+6))
    elif u:
        print('{} usec'.format(t / 1000))
    else:
        print('{} nsec'.format(t))


@lru_cache(maxsize=1024 * 1024)
def get_color(space, p):
    """Translate the pixel to a color."""

    return Color('srgb', [x / 255 for x in p[:3]], p[3] / 255 if len(p) > 3 else 1).convert(space, in_place=True)


def iter_image(img, space):
    """Process the image applying the requested filter."""

    with Image.open(img) as im:
        pixels = im.load()
        start = time.perf_counter_ns()
        total = im.size[0] * im.size[1]
        factor = 100 / total
        i = j = 0
        print('Pixels: {}'.format(total))
        print('> 0%', end='\r')
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                yield get_color(space, pixels[i, j])
            print('> {}%'.format(int((i * j) * factor)), end="\r")
        print('> 100%')
        t = time.perf_counter_ns() - start
        printt(t)


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='average_img', description='Get the average color of an image.')
    parser.add_argument('--input', '-i', help='Input image.')
    parser.add_argument('--space', '-s', default='srgb', help='Color space to average in.')
    parser.add_argument('--out-space', '-o', default='srgb', help='Color space to average in.')
    parser.add_argument('--premultiplied', '-p', action='store_true', help="Premultiply values.")
    args = parser.parse_args()

    print(
        Color.average(
            iter_image(args.input, args.space),
            space=args.space,
            premultiplied=args.premultiplied
        ).convert(args.out_space).to_string()
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
