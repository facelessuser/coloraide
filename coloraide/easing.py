"""
Easing functions.

https://drafts.csswg.org/css-easing/#easing-functions
https://probablymarcus.com/blocks/2015/02/26/using-bezier-curves-as-easing-functions.html
https://en.wikipedia.org/wiki/Horner%27s_method
https://en.wikipedia.org/wiki/Newton%27s_method

Since we know that control points P0 and P3 are always (0, 0) and (1, 1) respectively,
we can simplify the Bezier algorithm to:

```
x(t) = x0(1 - t)3 + 3x1(1 - t)2t + 3x2(1 - t)t2 + x3t3
x'(t) = 3(1 - t)2(x1 - x0) + 6(1 - t)t(x2 - x1) + 3t2(x3 - x2)
```

Further, they can be simplified to (Horner's method).

```
x(t) = (((1 - 3x2 + 3x1)t + 3x2 - 6x1)t + 3x1)t
x'(t) = 3(1 - 3x2 + 3x1)t2 + 2(3x2 - 6x1)t + 3x1
```

This allows us to calculate coefficients:

```
cx = 3.0 * p1x;
bx = 3.0 * (p2x - p1x) - cx;
ax = 1.0 - cx - bx;
```

And end up with:

```
x(t) = axt3 + bxt2 + cxt
x'(t) = 3axt2 + 2bxt + cx
```

This greatly simplifies things and makes it faster.
"""
import functools
from . import algebra as alg
from typing import Tuple, Callable

EPSILON = 1e-6
MAX_ITER = 10


def _bezier(t: float, a: float, b: float, c: float) -> float:
    """
    Calculate the bezier point.

    We know that P0 and P3 are always (0, 0) and (1, 1) respectively.
    Knowing this we can simplify the equation by precalculating them in.
    """

    return a * t ** 3 + b * t ** 2 + c * t


def _derivative_x(t: float, a: float, b: float, c: float) -> float:
    """Derivative of curve."""

    return 3 * a * t ** 2 + 2 * b * t + c


def _solve_bezier_x(target: float, a: float, b: float, c: float) -> float:
    """
    Solve curve to find a `t` that satisfies our desired `x`.

    Try a few rounds of Newton's method which is generally faster. If we fail,
    resort to binary search.
    """

    # Try Newtons method to see if we can find a suitable value
    i = 0
    t = target
    while i < MAX_ITER:
        # See how close we are to the desired `x`
        x = _bezier(t, a, b, c) - target
        if abs(x) < EPSILON:
            return t

        # Get the derivative, but bail if it is too small,
        # we will just keep looping otherwise.
        d = _derivative_x(t, a, b, c)
        if abs(d) < EPSILON:
            break

        # Calculate new time and try again
        t = t - x / d
        i += 1

    # Bisect until we arrive at a suitable value
    low, high = 0.0, 1.0
    t = target
    while abs(high - low) > EPSILON:
        x = _bezier(t, a, b, c)
        if (abs(x - target) < EPSILON):
            return t
        if x > target:
            high = t
        else:
            low = t
        t = (high + low) * 0.5

    # Just return whatever we got closest to
    return t


def _calc_bezier(target: float, a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
    """
    Calculate the y value of the bezier curve with the given `x`.

    The value given is actually the target `x`. We need to find a
    `t` that satisfies the `x` so that we can find the `y`.
    """

    # We'll never get a nice round 0 or 1 using the methods below,
    # but we know 0 and 1 should yield 0 and 1. Also, anything
    # beyond these bounds cannot be achieved.
    if target <= 0 or target >= 1:
        return alg.clamp(target, 0.0, 1.0)

    # Solve for `t` in relation to `x`
    t = _solve_bezier_x(target, a[0], b[0], c[0])

    # Use the found `t` to locate the `y`
    y = _bezier(t, a[1], b[1], c[1])
    return y


def cubic_bezier(x1: float, y1: float, x2: float, y2: float) -> Callable[..., float]:
    """Return a cubic bezier easing function."""

    if x1 < 0 or x1 > 1 or x2 < 0 or x2 > 1:
        raise ValueError("Cubic Bezier requires 'x' values to be between 0 - 1")

    # Precalculate the coefficients for Horner's method
    cx = 3.0 * x1
    bx = 3.0 * (x2 - x1) - cx
    ax = 1.0 - cx - bx

    cy = 3.0 * y1
    by = 3.0 * (y2 - y1) - cy
    ay = 1.0 - cy - by

    return functools.partial(_calc_bezier, a=(ax, ay), b=(bx, by), c=(cx, cy))


# CSS Easings Level 2
linear = cubic_bezier(0.25, 0.25, 0.75, 0.75)
ease = cubic_bezier(0.25, 0.1, 0.25, 1.0)
ease_in = cubic_bezier(0.42, 0.0, 1.0, 1.0)
ease_out = cubic_bezier(0.0, 0.0, 0.58, 1.0)
ease_in_out = cubic_bezier(0.42, 0.0, 0.58, 1.0)
