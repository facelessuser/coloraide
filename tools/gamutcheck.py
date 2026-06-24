"""Test gamut mapping response."""
import sys
import os
import argparse
import itertools as it
import json
import math

sys.path.insert(0, os.getcwd())

from coloraide.everything import ColorAll as Color
from coloraide import algebra as alg


def to_rect(coords, c, h):
    """Polar to rectangular."""

    coords[c], coords[h] = alg.polar_to_rect(coords[c], coords[h])
    return coords


def to_polar(coords, c, h):
    """Rectangular to rectangular."""

    coords[c], coords[h] = alg.rect_to_polar(coords[c], coords[h])
    return coords


def run(gamut, space, gmap, max_chroma, calc_near):
    """Test the gamut mapping algorithm noting the ∆L, ∆h, and the worst ∆h offender."""

    far_delta_h = max_delta_h = 0
    far_delta_l = max_delta_l = 0
    far_de = max_de = 0
    far_worst = worst = None
    lch = Color('white').convert(space)
    polar = lch._space.is_polar()
    if polar:
        l, c, h = lch._space.indexes()
        max_hue = lch._space.channels[h].high
        min_hue = lch._space.channels[h].low
        half_hue = max_hue / 2
        to_hue = max_hue / math.tau
    else:
        l, a, b = lch._space.indexes()
        max_hue = 360
        min_hue = 0
        half_hue = 180
        to_hue = 1
    scale = lch[l] / 100

    start = 0
    steps = 100
    for e, light in enumerate(alg.linspace(0.0, 100.0, steps, endpoint=False)):
        end = light
        for hue in alg.linspace(min_hue, max_hue, 360):
            coords = [0.0] * 3
            coords[l] = light * scale
            if polar:
                coords[c] = max_chroma
                coords[h] = hue
            else:
                coords[a] = max_chroma
                coords[b] = hue
                coords = to_rect(coords, a, b)
            c1 = Color(space, coords)
            c2 = c1.clone().fit(gamut, **gmap)
            assert c2.in_gamut(gamut), c2.convert(gamut).serialize()
            de = c1.delta_e(c2, method='2000')
            dl = (c1[l] - c2[l])
            if abs(dl) > abs(max_delta_l):
                max_delta_l = dl

            if de > max_de:
                max_de = de

            if polar:
                h1, h2 = c1[h], c2[h]
            else:
                coords = c1[:-1]
                h1 = to_polar(coords, a, b)[b]
                coords = c2[:-1]
                h2 = to_polar(coords, a, b)[b]
                if max_hue != 360:
                    h1 *= to_hue
                    h2 *= to_hue

            dh = (h1 % 360 - h2 % 360)
            if dh > half_hue:
                dh -= max_hue
            elif dh < -half_hue:
                dh += max_hue
            if abs(dh) > abs(max_delta_h):
                max_delta_h = dh
                worst = c1

        if e in (steps // 4, steps // 2, steps // (4 / 3), steps - 1):
            print(f'=== Far: Chroma {max_chroma} (Lightness {start} - {end}) ===')
            print('∆L =', max_delta_l)
            print('∆h =', max_delta_h)
            print('∆E =', max_de)
            print('Worst ∆h offender =>', worst)

            if abs(far_delta_h) > abs(max_delta_h):
                max_delta_h = far_delta_h
                worst = far_worst
            if abs(far_delta_l) > abs(max_delta_l):
                max_delta_l = far_delta_l
            if far_de > max_de:
                max_de = far_de

            far_delta_h = max_delta_h
            far_delta_l = max_delta_l
            far_de = max_de
            far_worst = worst

            max_delta_h = 0
            max_delta_l = 0
            max_de = 0
            worst = None
            start = end + 1

    if calc_near:
        gamut = 'srgb'
        for r, g, b in it.product(range(steps + 1), range(steps + 1), range(steps + 1)):
            c1 = Color('display-p3', [r / steps, g / steps, b / steps]).convert(space)
            c2 = c1.clone().fit(gamut, **gmap)
            assert c2.in_gamut(gamut), c2.convert(gamut).serialize()
            dl = (c1[l] - c2[l])
            if abs(dl) > abs(max_delta_l):
                max_delta_l = dl

            if polar:
                h1, h2 = c1[h], c2[h]
            else:
                coords = c1[:-1]
                h1 = to_polar(coords, a, b)[b]
                coords = c2[:-1]
                h2 = to_polar(coords, a, b)[b]
                if max_hue != 360:
                    h1 *= to_hue
                    h2 *= to_hue

            h1, h2 = c1[h], c2[h]
            dh = (h1 - h2)
            if dh > half_hue:
                dh -= max_hue
            elif dh < -half_hue:
                dh += max_hue
            if abs(dh) > abs(max_delta_h):
                max_delta_h = dh
                worst = c1

        print('=== Near: Display-P3 to sRGB ===')
        print('∆L =', max_delta_l)
        print('∆h =', max_delta_h)
        print('Worst ∆h offender =>', worst)

    if abs(far_delta_h) > abs(max_delta_h):
        max_delta_h = far_delta_h
        worst = far_worst
    if abs(far_delta_l) > abs(max_delta_l):
        max_delta_l = far_delta_l

    print('=== Final ===')
    print('∆L =', max_delta_l)
    print('∆h =', max_delta_h)
    print('Worst ∆h offender =>', worst)


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='gamutcheck.py',
        description='Check gamut mapping using ray tracing.'
    )
    # Flag arguments
    parser.add_argument(
        '--pspace', '-l',
        default='oklch',
        help="Perspetual space to use as the mapping space. If `pspace` of method is used, this will be ignored."
    )
    parser.add_argument(
        '--gamut', '-g', default='display-p3', help="Gamut to test.",
    )
    parser.add_argument(
        '--gmap', '-m', default='raytrace:{"pspace": "oklch"}', help="Specify GMA method to use (default is clip)."
    )
    parser.add_argument(
        '--max-chroma', '-c', type=float, default=0.8, help="Max chroma to test GMA with."
    )
    parser.add_argument(
        '--near', '-n', action='store_true', help="Calculate deltas when out of gamut color is close to boundary."
    )
    args = parser.parse_args()

    parts = [p.strip() if not e else json.loads(p) for e, p in enumerate(args.gmap.split(':', 1))]
    gmap = {'method': parts[0]}
    if len(parts) == 2:
        gmap.update(parts[1])

    pspace = gmap.get('pspace', args.pspace)
    run(args.gamut, pspace, gmap, args.max_chroma, args.near)

    return 0


if __name__ == "__main__":
    sys.exit(main())
