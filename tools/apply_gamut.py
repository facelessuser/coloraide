"""Modify a picture by increasing chroma and applying gamut mapping."""
from functools import lru_cache
from PIL import Image
from PIL import ImageCms
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
def apply_gamut_map(amount, p, gamut, fit, jnd, pspace):
    """Apply filter."""

    if jnd is not None:
        jnd = float(jnd)

    has_alpha = len(p) > 3
    color = Color(gamut, [x / 255 for x in p[:3]], p[3] / 255 if has_alpha else 1)
    if amount:
        color.set('oklch.c', lambda c: c * amount)
    # Fit the color back into the color gamut and return the results
    return tuple(
        int(x * 255)
        for x in color.convert('srgb').fit(method=fit, jnd=jnd, pspace=pspace)[:4 if has_alpha else -1]
    )


def process_image(img, output, amount, gamut, fit, jnd, pspace):
    """Process the image applying the requested filter."""

    with Image.open(img) as im:

        # Make sure we are writing in transparent mode for the opacity filter
        if im.format == 'PNG':
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
                pixels[i, j] = apply_gamut_map(amount, pixels[i, j], gamut, fit, jnd, pspace)
            print(f'> {int((i * j) * factor)}%', end="\r")
        print('> 100%')
        t = time.perf_counter_ns() - start
        printt(t)
        im.save(output, icc_profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes(), quality=100)


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='apply_gamut.py',
        description='Force higher chroma and apply gamut mapping to an image.'
    )
    parser.add_argument('--input', '-i', help='Input image.')
    parser.add_argument('--output', '-o', help='Output name and location.')
    parser.add_argument('--amount', '-a', type=float, help='Amount to increase chroma.')
    parser.add_argument('--gamut', default='srgb', help="Photo's current gamut.")
    parser.add_argument('--gamut-map', '-g', default="clip", help="Specify GMA method to use (default is clip).")
    parser.add_argument('--gamut-jnd', '-j', help="Adjust JND of old style chroma reduction.")
    parser.add_argument('--gamut-pspace', '-p', default="oklch", help="Specify perceptual space of ray trace method.")
    args = parser.parse_args()

    process_image(
        args.input,
        args.output,
        args.amount,
        args.gamut,
        args.gamut_map,
        args.gamut_jnd,
        args.gamut_pspace
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
