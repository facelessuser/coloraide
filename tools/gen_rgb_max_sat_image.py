"""Generate an image within an RGB space with saturated values for testing gamut mapping."""
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
from coloraide import algebra as alg


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


def generate_image(icc, output, width, height):
    """
    Generate the image by calculating maximum saturated colors.

    Colors are generated in HSL and converted to sRGB. The RGB values are simply
    treated like they are for the target RGB space.
    """

    if not icc:
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    else:
        profile = ImageCms.ImageCmsProfile(icc).tobytes()

    with Image.new(mode="RGB", size=(width, height)) as im:
        pixels = im.load()
        start = time.perf_counter_ns()
        total = im.size[0] * im.size[1]
        factor = 100 / total
        i = j = 0
        c = Color('hsl', [0, 1, 0.5])
        print(f'Pixels: {total}')
        print('> 0%', end='\r')
        for i in range(im.size[0]):
            c[0] = alg.lerp(0, 360, i / im.size[0])
            for j in range(im.size[1]):
                c[2] = alg.lerp(1, 0, j / im.size[1])
                pixels[i, j] = tuple(int(alg.clamp(x * 255, 0, 255)) for x in c.convert('srgb')[:-1])
            print(f'> {int((i * j) * factor)}%', end="\r")
        print('> 100%')
        t = time.perf_counter_ns() - start
        printt(t)
        im.save(output, icc_profile=profile, quality=100)


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='apply_gamut.py',
        description='Generate an image containing maximum saturation for a given RGB ICC profile.'
    )
    parser.add_argument('--icc', '-i', help='ICC profile.')
    parser.add_argument('--output', '-o', help='Output name and location.')
    parser.add_argument('--height', '-H', type=int, default=768, help="Height.")
    parser.add_argument('--width', '-W', type=int, default=1024, help="Width.")
    args = parser.parse_args()

    generate_image(
        args.icc,
        args.output,
        args.width,
        args.height
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
