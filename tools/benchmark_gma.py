"""Benchmark gamut mapping algorithms."""
import sys
import os
import argparse
import json
import time

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


def run_oklch(gamut, gmap, steps=0):
    """Run benchmark."""

    c = 0.4
    color = Color('oklch', [0, c, 0])

    count = 0
    n = abs(steps)
    total = n * n
    factor = 100 / total
    print(f'Colors: {total}')
    print('> 0%', end='\r')
    start = time.perf_counter_ns()
    for l in alg.linspace(0, 1, n):
        count += 1
        for h in alg.linspace(0, 360, n):
            color[:-1] = [l, c, h]
            color.fit(gamut, **gmap)
        count += n
        print(f'> {int(count * factor)}%', end="\r")
    print('> 100%')
    t = time.perf_counter_ns() - start
    printt(t)


def run_rec2020(gamut, gmap, steps=0):
    """Run benchmark."""

    hsl = Color('hsl', [0, 1, 0.5])
    rec2020 = Color('rec2020', [0, 0, 0])

    count = 0
    n = abs(steps)
    total = n * n
    factor = 100 / total
    print(f'Colors: {total}')
    print('> 0%', end='\r')
    start = time.perf_counter_ns()
    for l in alg.linspace(0, 1, n):
        count += 1
        for h in alg.linspace(0, 360, n):
            hsl[2] = l
            hsl[0] = h
            rec2020[:-1] = hsl.convert('srgb')[:-1]
            rec2020.fit(gamut, **gmap)
        count += n
        print(f'> {int(count * factor)}%', end="\r")
    print('> 100%')
    t = time.perf_counter_ns() - start
    printt(t)


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='benchmark_gma.py',
        description='Benchmark GMAs using different scenarios.'
    )
    # Flag arguments
    parser.add_argument(
        '--gamut', '-g', default='display-p3', help="Gamut to test.",
    )
    parser.add_argument('--gmap', '-m', default="clip", help="Specify GMA method to use (default is clip).")
    parser.add_argument(
        '--test', '-t', default="oklch", help="Test name."
    )
    parser.add_argument(
        '--steps', '-s', type=int, default=500, help="Steps."
    )
    args = parser.parse_args()

    parts = [p.strip() if not e else json.loads(p) for e, p in enumerate(args.gmap.split(':', 1))]
    gmap = {'method': parts[0]}
    if len(parts) == 2:
        gmap.update(parts[1])

    if args.test == 'oklch':
        run_oklch(args.gamut, gmap, args.steps)
    elif args.test == 'rec2020':
        run_rec2020(args.gamut, gmap, args.steps)

    return 0


if __name__ == "__main__":
    sys.exit(main())
