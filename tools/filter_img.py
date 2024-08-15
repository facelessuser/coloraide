"""Modify a picture with a given filter."""
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


GMAP = {}


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
def apply_filter(name, amount, space, method, p):
    """Apply filter."""

    has_alpha = len(p) > 3
    color = Color('srgb', [x / 255 for x in p[:3]], p[3] / 255 if has_alpha else 1)
    if method is not None:
        # This is a CVD filter that allows specifying the method
        color.filter(name, amount, space=space, in_place=True, method=method, out_space='srgb')
    else:
        # General filter.
        color.filter(name, amount, space=space, in_place=True, out_space='srgb')
    # Fit the color back into the color gamut and return the results
    return tuple(int(x * 255) for x in color.fit(**GMAP)[:4 if has_alpha else -1])


def process_image(img, output, name, amount, space, cvd_approach):
    """Process the image applying the requested filter."""

    with Image.open(img) as im:

        # Make sure we are writing in transparent mode for the opacity filter
        if im.format == 'PNG' and name == 'opacity':
            if im.mode not in ('RGBA',):
                im = im.convert('RGBA')

        pixels = im.load()
        start = time.perf_counter_ns()
        total = im.size[0] * im.size[1]
        factor = 100 / total
        i = j = 0
        print(f'Pixels: {total}')
        print('> 0%', end='\r')
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                pixels[i, j] = apply_filter(name, amount, space, cvd_approach, pixels[i, j])
            print(f'> {int((i * j) * factor)}%', end="\r")
        print('> 100%')
        t = time.perf_counter_ns() - start
        printt(t)
        im.save(output)


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='filter_img', description='Apply filter to an image.')
    parser.add_argument('--input', '-i', help='Input image.')
    parser.add_argument('--output', '-o', help='Output name and location.')
    parser.add_argument('--filter', '-f', help='The filter to use.')
    parser.add_argument('--amount', '-a', type=float, help='Amount to filter the image.')
    parser.add_argument('--cvd-approach', '-c', help='CVD approach to use.')
    parser.add_argument('--space', '-s', default='srgb-linear', help='Color space to filter in.')
    parser.add_argument('--gamut-map', '-g', default="clip", help="Specify GMA method to use (default simple clipping)")
    parser.add_argument('--gamut-options', '-G', default="{}", help="Define gamut mapping options.")

    args = parser.parse_args()

    global GMAP
    GMAP = {'method': args.gamut_map}
    GMAP.update(json.loads(args.gamut_options))

    process_image(
        args.input,
        args.output,
        args.filter,
        args.amount,
        args.space,
        args.cvd_approach
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
