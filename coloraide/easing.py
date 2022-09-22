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
from __future__ import annotations
import functools
from typing import Callable

EPSILON = 1e-6
# This value is honestly pretty arbitrary (was 10, now 8),
# probably would be good to test and find the optimal value.
MAX_ITER = 8


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

        # Getting too close zero or is zero
        if abs(d) < EPSILON:  # pragma: no cover
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
    # TODO: Is this needed? Can we actually ever hit this?
    return t  # pragma: no cover


def _extrapolate(t: float, p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """
    Extrapolate.

    Try to use the closest tangent to the endpoint, but if we can't,
    we'll just end up returning the same `t`.
    """

    # See if we can use the tangent of a point closest to P3
    if t > 1:
        slope = 1.0

        # Use a straight line through P2 and P3
        if p2[0] < 1:
            slope = (p2[1] - 1.0) / (p2[0] - 1.0)

        # Use a straight line through P1 and P3
        elif p1[0] < 1:
            slope = (p1[1] - 1.0) / (p1[0] - 1.0)

        intercept = 1.0 - slope

    # See if we can use the tangent of a point closest to P0
    else:
        slope = 1.0

        # Use a straight line through P1 and P0
        if p1[0] > 0.0:
            slope = p1[1] / p1[0]

        # Use a straight line through P2 and P0
        elif p2[0] > 0:
            slope = p2[1] / p2[0]

        intercept = 0.0

    return slope * t + intercept


def _calc_bezier(
    target: float,
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float]
) -> float:
    """
    Calculate the y value of the bezier curve with the given `x`.

    The value given is actually the target `x`. We need to find a
    `t` that satisfies the `x` so that we can find the `y`.
    """

    # We'll likely not get a nice round 0 or 1 using the methods below,
    # but we know 0 and 1 should yield 0 and 1, so shortcut out and
    # same some calculations.
    if target in (0, 1):
        return target

    # Extrapolate per the spec
    if target > 1 or target < 0:
        return _extrapolate(target, p1, p2)

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

    return functools.partial(_calc_bezier, a=(ax, ay), b=(bx, by), c=(cx, cy), p1=(x1, y1), p2=(x2, y2))


def linear(t: float) -> float:
    """Linear."""

    return t


# CSS Easings Level 2
ease = cubic_bezier(0.25, 0.1, 0.25, 1.0)
ease_in = cubic_bezier(0.42, 0.0, 1.0, 1.0)
ease_out = cubic_bezier(0.0, 0.0, 0.58, 1.0)
ease_in_out = cubic_bezier(0.42, 0.0, 0.58, 1.0)
