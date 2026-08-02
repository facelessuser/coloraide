"""Benchmark RYB conversion."""
import sys
import os
import argparse
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


def run_ryb(space, check, steps=0):
    """Run benchmark."""

    hsl = Color('hsl', [0, 1, 0.5])
    ryb = Color(space, [0, 0, 0])

    count = 0
    n = abs(steps)
    total = n * n
    factor = 100 / total
    print(f'Colors: {total}')
    print('> 0%', end='\r')
    start = time.perf_counter_ns()
    failed = 0
    for l in alg.linspace(0, 1, n):
        count += 1
        for h in alg.linspace(0, 360, n):
            hsl[2] = l
            hsl[0] = h
            ryb[:-1] = hsl.convert('srgb')[:-1]
            ryb2 = ryb.convert('srgb').convert(space, in_place=True)
            if check:
                s1, s2 = ryb.serialize(), ryb2.serialize()
                if s1 != s2:
                    failed += 1
                    print(f"FAIL: {s1} != {s2}")
        count += n
        print(f'> {int(count * factor)}%', end="\r")
    print('> 100%')
    t = time.perf_counter_ns() - start
    printt(t)
    print(f'FAILED: {failed} colors')


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='benchmark_ryb.py',
        description='Benchmark RYB.'
    )
    parser.add_argument('--check', '-c', action='store_true', help="Compared converted colors.")
    parser.add_argument('--ryb', '-r', default='ryb', help="RYB space.")
    parser.add_argument(
        '--steps', '-s', type=int, default=500, help="Steps."
    )
    args = parser.parse_args()

    run_ryb(args.ryb, args.check, args.steps)

    return 0


if __name__ == "__main__":
    sys.exit(main())
