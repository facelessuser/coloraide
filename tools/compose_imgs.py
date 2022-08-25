"""Apply compositing on images of the same size."""
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
def apply_compositing(background, blend, operator, pixels, fit, space):
    """Apply compositing."""

    color = Color('srgb', [x / 255 for x in pixels[0][:-1]], pixels[0][3] / 255)
    backdrops = [Color('srgb', [x / 255 for x in p[:3]], p[3] / 255) for p in pixels[1:]]
    color.compose(backdrops, blend=blend, operator=operator, in_place=True, space=space, out_space='srgb').clip()
    # Overlay first layer on background color in isolation
    if background != 'transparent':
        color.compose(background, in_place=True).clip()
    return tuple([int(x * 255) for x in color.fit(method=fit)[:4]])


def process_image(imgs, bg, output, blend, porter_duff, fit, space):
    """Process the image applying the requested blend mode and compositing operator."""

    images = []
    pixels = []
    size = None
    for i in imgs:
        img = Image.open(i)

        # Ensure we are working in `RGBA`
        if img.mode not in ('RGBA',):
            img = img.convert('RGBA')

        if size is None:
            size = img.size
        elif size != img.size:
            raise RuntimeError('Images must be of the same size')

        images.append(img)
        pixels.append(img.load())

    total = images[0].size[0]
    start = time.perf_counter_ns()
    x, y = images[0].size
    total = images[0].size[0] * images[0].size[1]
    factor = 100 / total

    # Compose the various layers
    i = j = 0
    print('Pixels: {}'.format(total))
    print('> 0%', end='\r')
    for e, i in enumerate(range(x)):
        for j in range(y):
            pixels[0][i, j] = apply_compositing(bg, blend, porter_duff, tuple([p[i, j] for p in pixels]), fit, space)
        print('> {}%'.format(int((e * j) * factor)), end="\r")
    print('> 100%')
    t = time.perf_counter_ns() - start
    printt(t)
    images[0].save(output)

    # Close images
    [img.close() for img in images]


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='compose_images.py', description='Apply compositing to a series of images.')
    parser.add_argument('--image', '-i', action='append', help='Image.')
    parser.add_argument('--output', '-o', help='Output file.')
    parser.add_argument('--porter-duff', '-p', default='source-over', help='Porter Duff compositing operator.')
    parser.add_argument('--blend', '-b', default='normal', help="The blend mode.")
    parser.add_argument('--space', '-s', default='srgb-linear', help="Space to compose in.")
    parser.add_argument(
        '--background-color', '-c',
        default='transparent',
        help="Background color. Blended in source-over in isolation."
    )
    parser.add_argument('--gamut-map', '-g', default="clip", help="Specify GMA method to use (default simple clipping)")
    args = parser.parse_args()

    process_image(
        args.image,
        args.background_color,
        args.output,
        args.blend,
        args.porter_duff,
        args.gamut_map,
        args.space
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
