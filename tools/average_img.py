"""Get the average color of an image."""
from functools import lru_cache
from PIL import Image
import time
import argparse
import sys
import os
import json

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
            print(f'{h} hours ', end='')
        if m:
            print(f'{m} minutes ', end='')
        print(f'{s} sec')
    elif m:
        print(f'{t / 1e+6} msec')
    elif u:
        print(f'{t / 1000} usec')
    else:
        print(f'{t} nsec')


@lru_cache(maxsize=1024 * 1024)
def get_color(space, p):
    """Translate the pixel to a color."""

    return Color('srgb', [x / 255 for x in p[:3]], p[3] / 255 if len(p) > 3 else 1).convert(space, in_place=True)


def iter_image(img, space, no_resize):
    """Process the image applying the requested filter."""

    with Image.open(img) as im:
        if im.format == 'PNG':
            if im.mode not in ('RGBA',):
                im = im.convert('RGBA')

        if not no_resize and (im.size[0] > 500 or im.size[1] > 500):
            factor = 500 / max(im.size)
            new_im = im.resize((max(1, int(im.size[0] * factor)), max(1, int(im.size[1] * factor))))
        else:
            new_im = im
        pixels = new_im.load()
        start = time.perf_counter_ns()
        total = new_im.size[0] * new_im.size[1]
        factor = 100 / total
        i = j = 0
        print(f'Pixels: {total}')
        print('> 0%', end='\r')
        for i in range(new_im.size[0]):
            for j in range(new_im.size[1]):
                yield get_color(space, pixels[i, j])
            print(f'> {int((i * j) * factor)}%', end="\r")
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
    parser.add_argument('--no-resize', '-r', action='store_true', help="Disable resizing of image.")
    parser.add_argument('--gmap', '-g', default="clip", help="Specify GMA method to use (default is clip).")
    args = parser.parse_args()

    parts = [p.strip() if not e else json.loads(p) for e, p in enumerate(args.gmap.split(':', 1))]
    gmap = {'method': parts[0]}
    if len(parts) == 2:
        gmap.update(parts[1])

    print(
        Color.average(
            iter_image(args.input, args.space, args.no_resize),
            space=args.space,
            premultiplied=args.premultiplied,
        ).convert(args.out_space).to_string(fit=gmap)
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
