"""
Math related methods.

Includes various math related functions to aid in color translation and manipulation.

Matrix method APIs are implemented often to mimic the familiar Numpy library or SciPy.
The API for a given function may look very similar to those found in either of the two
scientific libraries. Our intent is not implement a full matrix library, but mainly the
parts that are most useful for what we do with colors. Functions may not have all the
features as found in the aforementioned libraries, and the returns may vary in format,
and it also not guaranteed the algorithms behind the scene are identical, but the API should
be similar.

We actually really like Numpy and SciPy, and have only done this to keep dependencies lightweight
and available on non C Python based implementations.

There is no requirement that external plugins need to use `algebra` and Numpy and SciPy could
used as long as the final results are converted to normal types.
"""
from __future__ import annotations
import builtins
import bisect
import decimal
import sys
import cmath
import math
import operator
import functools
import itertools as it
from .types import (
    Number, StrictNumber, Shape, DimHints, EmptyShape, VectorShape, MatrixShape, TensorShape, ArrayShape,
    VectorT, MatrixT, TensorT, ArrayT, VectorTLike, MatrixTLike, TensorTLike, ArrayTLike
)
from typing import Callable, Sequence, Iterator, Any, overload, Generic, Literal, cast

EPS = sys.float_info.epsilon
RTOL = 4 * EPS
ATOL = 1e-12
NaN = math.nan
INF = math.inf
MAX_10_EXP = sys.float_info.max_10_exp
MIN_FLOAT = sys.float_info.min
MAX_FLOAT = sys.float_info.max

# Keeping for backwards compatibility
_all = builtins.all
_any = builtins.any

# Shortcut for math operations
# Specify one of these in divide, multiply, dot, etc.
# to bypass analyzing the shape to determine which path
# to take.
#
# `SC` = scalar, `D1` = 1-D array or vector, `D2` = 2-D
# matrix, and `DN` is N-D matrix, which could be of any size,
# even greater than 2-D.
#
# If just a single specifier is used, it is assumed that
# the operation is performed against another of the same.
# `SC` = scalar and a scalar, while `SC_D1` means a scalar
# and a vector
#
# For any combination with an N-D matrix, you can just use ND as
# we must determine the shape of the N-D matrix anyway in order
# to process it, so checking the shape cannot be avoided.
SC = (0, 0)
D1 = (1, 1)
D2 = (2, 2)
DN = (-1, -1)
SC_D1 = (0, 1)
SC_D2 = (0, 2)
D1_SC = (1, 0)
D1_D2 = (1, 2)
D2_SC = (2, 0)
D2_D1 = (2, 1)
DN_DM = (-1, -1)

# Vector used to create a special matrix used in natural splines
M141 = [1, 4, 1]

# QR decomposition modes
QR_MODES = {'reduced', 'complete', 'r', 'raw'}


################################
# General math
################################
def sgn(x: StrictNumber) -> StrictNumber:
    """Return the sign of a given value."""

    if isinstance(x, int):
        return 1 if x > 0 else -1 if x < 0 else 0
    return 1.0 if x > 0.0 else -1.0 if x < 0 else x


def order(x: StrictNumber) -> int:
    """Get the order of magnitude of a number."""

    _, digits, exponent = decimal.Decimal(x).as_tuple()
    return len(digits) + int(exponent) - 1


def round_half_up(n: StrictNumber, scale: int = 0) -> float:
    """Round half up."""

    if not isinstance(scale, int):
        raise ValueError("'float' object cannot be interpreted as an integer")

    # Generally, Python reports the minimum float as 2.2250738585072014e-308,
    # but there are outliers as small as 5e-324. `mult` is limited by a scale of 308
    # due to overflow, but we could calculate greater values by splitting the `mult`
    # factor into two smaller factors when the scale exceeds 308. This would allow us
    # to round out to 324 decimal places for really small values like 5e-324, but
    # these values simply aren't practical enough to warrant the extra effort.
    mult = 10.0 ** scale
    return math.floor(n * mult + 0.5) / mult


def _round_location(
    f: StrictNumber,
    p: int = 0,
    mode: str = 'digits'
) -> tuple[int, int]:
    """Return the start of the first significant digit and the digit targeted for rounding."""

    # Round to number of digits
    if mode == 'digits':
        # Less than zero we assume double precision
        if p < 0:
            p = 17
        d = p
        # If zero, assume integer rounding
        if p == 0:
            p = 17

    # Round to decimal place
    elif mode == 'decimal':
        d = p
        p = MAX_10_EXP

    # Round of significant digits
    elif mode == 'sigfig':
        d = MAX_10_EXP
        # Less than zero we assume double precision
        if p < 0 or p > 17:
            p = 17
        # If zero, assume integer rounding
        elif p == 0:
            p = 17
            d = 0

    else:
        raise ValueError("Unknown rounding mode '{mode}'")

    if f == 0 or not math.isfinite(f):
        return 0, 0

    # Round to specified significant figure or fractional digit, which ever is less
    v = -math.floor(math.log10(abs(f)))
    p = v + (p - 1)
    return v, d if d < p else p


def round_to(
    f: StrictNumber,
    p: int = 0,
    mode: str = 'digits',
    rounding: Callable[[StrictNumber, int], float]=round_half_up
) -> float:
    """Round to the specified precision using "half up" rounding by default."""

    _, p = _round_location(f, p, mode)

    # Return non-finite values without further processing
    if not math.isfinite(f):
        return f

    # Round to the specified location using the specified rounding function
    return rounding(f, p)


def clamp(
    value: StrictNumber,
    mn: StrictNumber | None = None,
    mx: StrictNumber | None = None
) -> StrictNumber:
    """Clamp the value to the given minimum and maximum."""

    if mx is not None and value > mx:
        value = mx
    if mn is not None and value < mn:
        value = mn
    return value


def zdiv(a: StrictNumber, b: StrictNumber, default: float = 0.0) -> float:
    """Protect against zero divide."""

    if b == 0:
        return default
    return a / b


def cbrt(n: StrictNumber) -> float:
    """Calculate cube root."""

    return nth_root(n, 3)


def nth_root(n: StrictNumber, p: StrictNumber) -> float:
    """Calculate nth root while handling negative numbers."""

    if p == 0:  # pragma: no cover
        return math.inf

    if n == 0:
        # Can't do anything with zero
        return 0.0

    return math.copysign(abs(n) ** (p ** -1), n)


def spow(base: StrictNumber, exp: StrictNumber) -> float:
    """Perform `pow` with signed number."""

    return math.copysign(abs(base) ** exp, base)


def rect_to_polar(a: StrictNumber, b: StrictNumber) -> tuple[float, float]:
    """Take rectangular coordinates and make them polar."""

    return math.sqrt(a * a + b * b), math.degrees(math.atan2(b, a)) % 360


def polar_to_rect(c: StrictNumber, h: StrictNumber) -> tuple[float, float]:
    """Take rectangular coordinates and make them polar."""

    r = math.radians(h)
    return c * math.cos(r), c * math.sin(r)


def reversed_bisect_left(a: VectorT[Number], x: float, lo: int = 0, hi: int | None = None) -> int:
    """Perform bisect left on a reversed list."""

    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x >= a[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo


def solve_bisect(
    a: float,
    b: float,
    f: Callable[..., float],
    args: tuple[Any, ...] | tuple[()] = (),
    maxiter: int = 50,
    rtol: float = RTOL,
    atol: float = ATOL,
) -> tuple[float, bool]:
    """
    Apply the bisect method to converge upon an answer.

    Return the best answer based on the specified limits and also
    return a boolean indicating if we confidently converged.
    """

    t = math.nan
    x = math.nan

    # If the answer is close to the bounds, return best value without iterating.
    x1 = f(a, *args) if args else f(a)
    if math.isclose(x1, 0, rel_tol=rtol, abs_tol=atol):
        return a, True
    x2 = f(b, *args) if args else f(b)
    if math.isclose(x2, 0, rel_tol=rtol, abs_tol=atol):
        return b, True

    if x1 > 0:
        a, b = b, a
    dt = b - a


    # Exit if the bounds do not contain the solution
    if sgn(x1) == sgn(x2):
        return t, False

    for _ in range(maxiter):
        dt *= 0.5
        t = a + dt
        x = f(t, *args) if args else f(t)

        # Update bounds
        if sgn(x) != sgn(t):
            a = t

        if math.isclose(x, 0, rel_tol=rtol, abs_tol=atol):
            return t, True

    return t, math.isclose(x, 0, rel_tol=rtol, abs_tol=atol)  # pragma: no cover


def _solve_quadratic(poly: VectorTLike[float]) -> VectorT[float]:
    """
    Solve a quadratic equation.

    The vector represents the polynomial coefficients of an equation set to zero.

    All non-real roots are filtered out at the end.
    """

    a, b, c = poly

    # Scale coefficients by `a` so that `a` is 1 and drops out of future calculations
    if a != 1:
        b /= a
        c /= a

    m = -b * 0.5
    # Calculate the discriminant to determine number of roots and what type
    discriminant = m ** 2 - c
    # With `a` no longer a factor, we can greatly simplify the traditional quadratic formula
    # Solutions: `m +/- (m ** 2 - c) ** (1/2)`
    if discriminant < 0:
        # No real roots
        return []
    elif discriminant > 0:
        # Two real roots
        r = math.sqrt(discriminant)
        return [
            m + r,
            m - r
        ]
    # Double root
    return [m]


def _solve_cubic(poly: VectorTLike[float]) -> VectorT[float]:
    """
    Solve a cubic equation using Cardano's Method.

    The vector represents the polynomial coefficients of an equation set to zero.

    All non-real roots are filtered out at the end.

    https://en.wikipedia.org/wiki/Cubic_equation#Cardano's_formula
    """

    a, b, c, d = poly

    # Scale coefficients by `a` so that `a` is 1 and drops out of future calculations
    if a != 1:
        b /= a
        c /= a
        d /= a

    # Transform equation to a form removing the squared term: `t^3 + pt + q = 0`
    p = (3 * c - b ** 2) / 3
    q = (2 * b ** 3 - 9 * b * c + 27 * d) / 27

    # Calculate the discriminant to determine number of roots and what type
    discriminant = (q ** 2 / 4 + p ** 3 / 27)

    # Calculate `t = u^(1/3) + v^(1/3)`
    # Cube root must not use `** (1 / 3)` if real.
    # Should use `math.cbrt` or some signed power equivalent
    # on systems that don't support it.
    r = cmath.sqrt(discriminant)
    u3 = -q / 2 + r
    v3 = -q / 2 - r
    u = u3 ** (1 / 3) if u3.imag else nth_root(u3.real, 3)
    v = v3 ** (1 / 3) if v3.imag else nth_root(v3.real, 3)
    t = u + v

    # Precalculate offset for conversion from `t` back to `x`
    # `x = t - b / 3` -> `x = t - k`
    k = b / 3

    # Primitive roots: `pr = (-1 +/- -3 ** (1/2)) / 2 ~= -0.5 +/- 0.8660254037844386j`
    # The complex part (`prc`) equivalent calculation: `(0.8660254037844386j) = 3 ** (1/2) / 2j`
    prc = cmath.sqrt(3) / 2j

    # We can find the other two roots by multiplying u and v with the primitive roots:
    # ```
    # t2 = pr1 * u + pr2 * v
    # t3 = pr2 * u + pr1 * v
    # ```
    # With some algebraic manipulation and factoring the conversion to `x`
    # ```
    # x1 = (v + v) - k
    # x2 = -0.5 * (u + v) + (u - v) * prc - k
    # x3 = -0.5 * (u + v) - (u - v) * prc - k
    # ```
    td = u - v
    # Convert `t` back to `x`
    x = t - k
    if discriminant > 0:
        # One real root
        return [x.real]
    elif discriminant < 0:
        # Three real roots
        return [
            x.real,
            (-0.5 * t + td * prc - k).real,
            (-0.5 * t - td * prc - k).real
        ]
    # Three real roots, two of which are doubles
    return [
        x.real,
        (-0.5 * t + td * prc - k).real
    ]


def solve_nth_poly(
    coef: VectorTLike[float],
    guess: float = 0.5,
    maxiter: int = 50,
    rtol: float = RTOL,
    atol: float = ATOL
) -> VectorT[float]:
    """
    Solve polynomial of nth degree.

    Takes a polynomial of any degree greater outputs all real roots (assuming it can find them).

    Approach uses Newton's method to find a root and then uses synthetic division to reduce the degree
    of the polynomial simplifying the solution for the next root. If the degree falls below 4, solve
    the for the remaining roots using more precise approaches.

    Newton's method is not guaranteed to converge. If we can no longer converge upon roots, give up,
    assuming there are no more real roots, even if that is not true.
    """

    roots = []  # type: VectorT[float]
    while len(coef) > 4:
        root, status = solve_newton(
            guess,
            lambda x, coef=coef: sum([c * x ** i for i, c in enumerate(coef[::-1], 0)]),
            lambda x, coef=coef: sum([i * c * x ** (i - 1) for i, c in enumerate(coef[-2::-1], 1)]),
            maxiter=maxiter,
            rtol=rtol,
            atol=atol
        )

        # Can't find any more roots
        if not status:
            break

        roots.append(root)

        # Perform synthetic division to reduce the order of the equation
        quotient = [coef[0]]
        for c in coef[1:]:
            quotient.append(quotient[-1] * root + c)
        # Ignore remainder
        quotient.pop()
        coef = quotient

    # Solve the rest with lower order approaches
    if 4 >= len(coef) > 1:
        roots.extend(solve_poly(coef))

    return roots


def solve_poly(poly: VectorTLike[float]) -> VectorT[float]:
    """
    Solve the given polynomial.

    Currently, only up to 3rd degree polynomials are supported.
    """

    # Remove leading zeros and/or demote polynomial if leading values
    # are very small to avoid floating point numerical instability.
    count = 0
    for pi in poly:
        if abs(pi) < ATOL:
            count += 1
            continue
        break
    if count:
        poly = poly[count:]

    # Select the appropriate solver
    l = len(poly)
    if l > 4:
        return solve_nth_poly(poly)
    elif l == 4:
        return _solve_cubic(poly)
    elif l == 3:
        return _solve_quadratic(poly)
    elif l == 2:
        return [-poly[1] / poly[0]]
    return []


def solve_newton(
    x0: float,
    f0: Callable[..., float],
    dx: Callable[..., float],
    dx2: Callable[..., float] | None = None,
    args: tuple[Any, ...] | tuple[()] = (),
    maxiter: int = 50,
    rtol: float = RTOL,
    atol: float = ATOL,
    order: int = 2,
    bounds: tuple[float, float] | None = None,
) -> tuple[float, bool | None]:
    """
    Solve equation using Newton's method.

    If order <= 3 and second derivative is given, Halley's method will be used as an additional step.
    Newton provides 2nd order convergence and Halley provides 3rd order convergence.

    ```
    newton = yn = xn - f(xn) / f'(xn)
    halley = xn - 2 f(xn) f'(xn) / (2 f'(xn)^2 - f(xn) f''(xn))
    ```

    Algebraically, we can pull the Newton stop out of the Halley method into two separate steps
    that can be applied on top of each other.

    ```
    Step1: halley = xn - f(xn) * f'(xn) / (f'(xn) ** 2 - 0.5 * f(xn) * f''(xn))
    Step2: yn = f(xn) / f'(xn)
    Step3: halley = xn - f(xn) / (f'(xn) - (0.5 * yn * f''(xn))
    Step4: halley = xn - yn / (1 - 0.5 * yn * f''(xn) / f'(xn))
    ```

    If order == 3 and 2nd derivative is not provided, we can use Traub's method which gives 3rd order convergence
    without a second derivative.

    ```
    yn = xn - f(xn) / f'(xn)
    traub = yn - f(yn) / f'(xn)
    ```

    If order >= 3, we can use Ostrowski method where only one derivative is needed, but you can get 4th order
    convergence.

    ```
    yn = xn - f(xn) / f'(xn)
    ostrowski = yn - f(xn) / (f(xn) - 2 * f(yn)) * (f(yn) / f'(xn))
    ```

    Return result along with True if converged, False if did not converge, None if could not converge.
    """

    if dx2 is not None and order < 3:
        order = 3

    slow = False
    if bounds is not None:
        a, b = bounds

        # If the answer is close to the bounds, return best value without iterating.
        fx1 = f0(a, *args) if args else f0(a)
        if math.isclose(fx1, 0, rel_tol=rtol, abs_tol=atol):
            return a, True

        fx2 = f0(b, *args) if args else f0(b)
        if math.isclose(fx2, 0, rel_tol=rtol, abs_tol=atol):
            return b, True

        # Exit if the bounds do not contain the solution
        if fx1 and fx2 and sgn(fx1) == sgn(fx2):
            return math.nan, False

        if fx1 > 0:
            a, b = b, a

        dx_last = abs(b - a)

        bracketed = True
    else:
        a, b = -math.inf, math.inf
        bracketed = False
        dx_last = 0

    for _ in range(maxiter):
        # Get result form equation when setting value to expected result
        fx = f0(x0, *args) if args else f0(x0)
        prev = x0

        in_bounds = True if not bracketed else a <= x0 <= b

        # If the result is zero, we've converged
        if fx == 0 and in_bounds:
            return x0, True

        d1 = dx(x0, *args) if args else dx(x0)

        # Update brackets
        if bracketed:
            if in_bounds:
                if fx < 0:
                    a = x0
                else:
                    b = x0
            slow = abs(2.0 * fx) > abs(dx_last * d1)
            dx_last = d1

        # Cannot find a solution if derivative is zero
        if abs(d1) < ATOL or slow:
            # Try to bisect to a different location
            if bracketed:
                x0 = a + (b - a) * 0.5
                if x0 != prev:
                    continue
            return x0, None

        # Newton step
        newton = fx / d1

        if order == 3:
            # Halley's method: 3rd order convergence.
            if dx2 is not None:
                d2 = dx2(x0, *args) if args else dx2(x0)
                denom = 1 - (0.5 * newton * d2) / d1
                if abs(denom) >= ATOL:
                    newton /= denom

            # Traub's method: 3rd order convergence
            else:
                fy = f0(x0 - newton, *args) if args else f0(x0 - newton)
                newton -= fy / d1

        # Apply the Newton step (or adjusted Newton step)
        x0 -= newton

        # Ostrowski's method: 4th order convergence
        if order == 4:
            fy = f0(x0, *args) if args else f0(x0)
            denom = fx - 2 * fy
            if abs(denom) >= ATOL:
                x0 -= fx / denom * (fy / d1)

        # Value not in bracketed range, try to bisect
        if bracketed and not a <= x0 <= b:  # pragma: no cover
            x0 = a + (b - a) * 0.5
            if x0 != prev:
                continue
            return x0, None

        # Result is close enough
        if math.isclose(x0, prev, rel_tol=rtol, abs_tol=atol):
            return x0, True

    return x0, False  # pragma: no cover


################################
# Interpolation and splines
################################
def lerp(p0: float, p1: float, t: float) -> float:
    """Linear interpolation."""

    return p0 + (p1 - p0) * t


def ilerp(p0: float, p1: float, t: float) -> float:
    """Inverse interpolation."""

    d = (p1 - p0)
    return (t - p0) / d if abs(d) > ATOL else 0


def bilerp(p0: float, p1: float, p2: float, p3: float, tx: float, ty: float) -> float:
    """Bilinear interpolation."""

    return lerp(lerp(p0, p1, tx), lerp(p2, p3, tx), ty)


def lerp2d(vertices: MatrixT[float], t: VectorT[float]) -> VectorT[float]:
    """
    Interpolate in 2D.

    Vertices should be in column form [[x...], [y...]].
    """

    return [bilerp(*vertices[i], *t) for i in range(2)]


def ilerp2d(
    vertices: MatrixT[float],
    point: VectorT[float],
    *,
    guess: VectorT[float] | None = None,
    max_iter: int = 20,
    tol: float = ATOL
) -> VectorT[float]:
    """
    Inverse interpolation of a 2D point.

    Same algorithm as `ilerp3d` just for a 2D point. Based off the forward transform below.

    ```
    vxy = v00 (1 - x) (1 - y) +
          v10 x (1 - y) +
          v01 (1 - x) y +
          v11 x y
    ```
    """

    # Initial guess
    xy = guess if guess is not None else [0.5, 0.5]

    try:
        for _ in range(max_iter):

            # Calculate the residual by using our guess to calculate the what should be the input and compare
            residual = subtract(lerp2d(vertices, xy), point, dims=D1)

            # If we are close enough to our input, we can quit
            if math.sqrt(residual[0] ** 2 + residual[1] ** 2) < tol:
                break

            # Build up the Jacobian matrix so we can solve for the next, closer guess.
            x, y = xy

            wx = 1 - x
            wy = 1 - y

            # Take the partial derivative of v000 - v111:
            # ```
            # [[f1 / dx, f1 / dy],
            #  ...,
            #  [f4 / dx, f4 / dy]]
            # ```
            m = [
                [-wy, -wx],
                [wy,  -x],
                [-y,  wx],
                [y,   x]
            ]

            j = matmul(vertices, m, dims=D2)

            # Solve for new guess
            xy = subtract(xy, solve(j, residual), dims=D1)
    except ValueError:  # pragma: no cover
        # The Jacobian matrix shouldn't fail inversion if we are in range.
        # Out of range may give us values we cannot invert. There are potential
        # ways to handle this to try and get moving again, but currently, we
        # just give up. We do not guarantee out of gamut conversions.
        pass

    return xy


def trilerp(
    p0: float,
    p1: float,
    p2: float,
    p3: float,
    p4: float,
    p5: float,
    p6: float,
    p7: float,
    tx: float,
    ty: float,
    tz: float
) -> float:
    """Trilinear interpolation."""

    return lerp(bilerp(p0, p1, p2, p3, tx, ty), bilerp(p4, p5, p6, p7, tx, ty), tz)


def lerp3d(
    vertices: MatrixT[float],
    t: VectorT[float]
) -> VectorT[float]:
    """
    Interpolation in 3D.

    Vertices should be in column form [[x...], [y...], [z...]].
    """

    return [trilerp(*vertices[i], *t) for i in range(3)]


def ilerp3d(
    vertices: MatrixT[float],
    point: VectorT[float],
    *,
    guess: VectorT[float] | None = None,
    max_iter: int = 50,
    tol: float = ATOL
) -> VectorT[float]:
    """
    Inverse trilinear interpolation.

    Uses Gauss-Newton method to compute the inverse of the trilinear interpolation.

    Original code by Nick Alger https://stackoverflow.com/a/18332009/3609487
    and adapted for our purposes. As stated in the link:

    > I release the 3D code to the public domain as well if anyone wants to use it.
    > - Nick Alger Jun 27, 2014 at 7:30

    Utilizes the trilinear interpolation method found here to get the inverse:
    http://paulbourke.net/miscellaneous/interpolation/. Results are the same as
    what we do in the forward, but easier to use for the inverse calculations.
    Forward transform found below with vertices ordered to match the order we store our
    vertices in.

    ```
    Vxyz = V000 (1 - x) (1 - y) (1 - z) +
           V100 x (1 - y) (1 - z) +
           V010 (1 - x) y (1 - z) +
           V110 x y (1 - z) +
           V001 (1 - x) (1 - y) z +
           V101 x (1 - y) z +
           V011 (1 - x) y z +
           V111 x y z
    ```
    """

    # Initial guess.
    xyz = guess if guess is not None else [0.5, 0.5, 0.5]

    try:
        for _ in range(max_iter):

            # Calculate the residual by using our guess to calculate the what should be the input and compare
            residual = subtract_x3(lerp3d(vertices, xyz), point, dims=D1)

            # If we are close enough to our input, we can quit
            if math.sqrt(residual[0] ** 2 + residual[1] ** 2 + residual[2] ** 2) < tol:
                break

            # Build up the Jacobian matrix so we can solve for the next, closer guess
            x, y, z = xyz
            wx = 1 - x
            wy = 1 - y
            wz = 1 - z

            # Take the partial derivative of v000 - v111:
            # ```
            # [[f1 / dx, f1 / dy, f1 / dz],
            #  ...,
            #  [f8 / dx, f8 / dy, f8 / dz]]
            # ```
            m = [
                [-wy * wz, -wx * wz, -wx * wy],
                [wy * wz,  -x * wz,  -x * wy],
                [-y * wz,  wx * wz,  -wx * y],
                [y * wz,   x * wz,   -x * y],
                [-wy * z,  -wx * z,  wx * wy],
                [wy * z,   -x * z,   x * wy],
                [-y * z,   wx * z,   wx * y],
                [y * z,    x * z,    x * y]
            ]

            j = matmul(vertices, m, dims=D2)

            # Solve for new guess
            xyz = subtract_x3(xyz, solve(j, residual), dims=D1)
    except ValueError:  # pragma: no cover
        # The Jacobian matrix shouldn't fail inversion if we are in range.
        # Out of range may give us values we cannot invert. There are potential
        # ways to handle this to try and get moving again, but currently, we
        # just give up. We do not guarantee out of gamut conversions.
        pass

    return xyz


class Interpolator:
    """Interpolation object."""

    def __init__(
        self,
        points: list[VectorT[float]],
        domain: VectorTLike[float] | None,
        extrapolate: bool = True,
        **kwargs: Any
    ) -> None:
        """Initialize."""

        self.length = len(points)
        self.num_coords = len(points[0])
        self.extrapolate = extrapolate
        self.preprocess(points, **kwargs)
        self.points = [*zip(*points)]
        self.domain = list(domain) if domain is not None else domain
        self.increasing = not self.domain or len(self.domain) == 1 or self.domain[1] > self.domain[0]

    @classmethod
    def preprocess(cls, points: list[VectorT[float]], **kwargs: Any) -> None:
        """Apply any preprocessing points."""

        pass

    def steps(self, count: int) -> list[VectorT[float]]:
        """Generate steps."""

        divisor = count - 1
        return [self(r / divisor) for r in range(0, count)]

    def run(self, i: int, t: float) -> VectorT[float]:
        """Begin interpolation."""

        coord = []
        for idx in range(self.num_coords):
            c = self.points[idx]
            coord.append(lerp(c[i], c[i + 1], t))
        return coord

    def handle_domain(self, t: float) -> float:
        """Scale the interpolation factor based on the domain."""

        if self.domain is None:
            return t

        import operator as op
        le, ge = (op.le, op.ge) if self.increasing else (op.ge, op.le)

        # Extrapolation
        if le(t, self.domain[0]):
            t = (t - self.domain[0]) / (self.domain[-1] - self.domain[0])
        elif ge(t, self.domain[-1]):
            t = 1.0 + (t - self.domain[-1]) / (self.domain[-1] - self.domain[0])

        # Interpolation
        else:
            bisect_left = bisect.bisect_left if self.increasing else reversed_bisect_left
            regions = len(self.domain) - 1
            size = (1 / regions)
            index = bisect_left(self.domain, t) - 1
            a, b = self.domain[index:index + 2]
            l = b - a
            adjusted = ((t - a) / l) if l else 0.0
            t = size * index + (adjusted * size)
        return t

    def __call__(self, t: float) -> VectorT[float]:
        """Interpolate."""

        t = self.handle_domain(t)
        n = self.length - 1
        i = max(min(math.floor(t * n), n - 1), 0)
        t = (t - i / n) * n if 0 <= t <= 1 else t
        if not self.extrapolate:
            t = clamp(t, 0.0, 1.0)

        return self.run(i, t)


class _CubicInterpolator(Interpolator):
    """Cubic interpolator."""

    DEF_END_COND = 'not-a-knot'

    def __init__(
        self,
        points: list[VectorT[float]],
        domain: VectorTLike[float] | None,
        **kwargs: Any
    ) -> None:
        """Initialize."""

        self.end_condition = kwargs.get('end_cond', self.DEF_END_COND)
        super().__init__(points, domain, **kwargs)

    @classmethod
    def preprocess(cls, points: list[VectorT[float]], end_cond: str | None = None, **kwargs: Any) -> None:
        """Apply any preprocessing points."""

        if end_cond is None:
            end_cond = cls.DEF_END_COND

        if end_cond == 'natural' or len(points) == 2:
            points.insert(0, [2 * a - b for a, b in zip(points[0], points[1])])
            points.append([2 * a - b for a, b in zip(points[-1], points[-2])])
        elif end_cond == 'not-a-knot':
            points.insert(0, [2 * a - b for a, b in zip(points[0], points[2])])
            points.append([2 * a - b for a, b in zip(points[-1], points[-3])])
        else:
            raise ValueError(f"End condition '{end_cond}' is not recognized")

    @staticmethod
    def interpolate(p0: float, p1: float, p2: float, p3: float, t: float) -> float:  # pragma: no cover
        """Interpolate."""

        raise NotImplementedError('This function is not implemented')

    def run(self, i: int, t: float) -> VectorT[float]:
        """Begin interpolation."""

        coord = []
        for idx in range(self.num_coords):
            c = self.points[idx]
            coord.append(
                self.interpolate(
                    c[i],
                    c[i + 1],
                    c[i + 2],
                    c[i + 3],
                    t
                )
            )
        return coord


class CatmullRomInterpolator(_CubicInterpolator):
    """Catmull-Rom interpolator."""

    @staticmethod
    def interpolate(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
        """Calculate the new point using the provided values."""

        # Save some time calculating this once
        t2 = t ** 2
        t3 = t2 * t

        # Insert control points to algorithm
        return (
            (-t3 + 2 * t2 - t) * p0 +  # B0
            (3 * t3 - 5 * t2 + 2) * p1 +  # B1
            (-3 * t3 + 4 * t2 + t) * p2 +  # B2
            (t3 - t2) * p3  # B3
        ) / 2


class MonotoneInterpolator(_CubicInterpolator):
    """Monotone interpolator."""

    @staticmethod
    def interpolate(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
        """
        A monotonic cubic Hermite sampler spline.

        This samples data of a points neighbors to calculate gradients and secants on the fly to
        create a monotonic cubic Hermite spline. Calculations could be done ahead of time and stored
        at the cost of memory, but we've opted to do this on the fly.

        We calculate our secants for our four samples (the center pair being our interpolation target).
        From those, we calculate an initial gradient, and test to see if it is needed. In the event
        that our there is no increase or decrease between the point, we can infer that the gradient
        should be horizontal. We also test if they have opposing signs, if so, we also consider the
        gradient to be zero.

        This is an alternative that assumes a cube with corners defined at (0,0) and (3,3) instead of
        a circle with radius 3. Both approaches encapsulate the entire monotonicity, but the cube
        approach requires less points and less checks and is more efficient for on the fly calculations.

        Once gradients are calculated, we simply perform the Hermite spline calculation and clean up
        floating point math errors to ensure monotonicity.

        - http://jbrd.github.io/2020/12/27/monotone-cubic-interpolation.html
        - https://www.jstor.org/stable/2156610
        - https://ui.adsabs.harvard.edu/abs/1990A%26A...239..443S/abstract
        - https://www.researchgate.net/publication/2511970_Non-Overshooting_Hermite_Cubic_Splines_For_Keyframe_Interpolation
        - https://en.wikipedia.org/w/index.php?title=Monotone_cubic_interpolation&oldid=950478742
        """

        # Save some time calculating this once
        t2 = t ** 2
        t3 = t2 * t

        # Calculate the secants for the differing segments
        s0 = p1 - p0
        s1 = p2 - p1
        s2 = p3 - p2

        # Calculate initial gradients
        m0 = (s0 + s1) * 0.5
        m1 = (s1 + s2) * 0.5

        # Center segment should be horizontal as there is no increase/decrease between the two points
        if math.isclose(p1, p2, rel_tol=RTOL, abs_tol=ATOL):
            m0 = m1 = 0.0
        else:

            # Gradient is zero if segment is horizontal or if the left hand secant differs in sign from current.
            if math.isclose(p0, p1, rel_tol=RTOL, abs_tol=ATOL) or sign(s0) != sign(s1):
                m0 = 0.0

            # Ensure gradient magnitude is either 3 times the left or current secant (smaller being preferred).
            else:
                m0 *= min(3.0 * s0 / m0, 3.0 * s1 / m0, 1.0)

            # Gradient is zero if segment is horizontal or if the right hand secant differs in sign from current.
            if math.isclose(p2, p3, rel_tol=RTOL, abs_tol=ATOL) or sign(s1) != sign(s2):
                m1 = 0.0

            # Ensure gradient magnitude is either 3 times the current or right secant (smaller being preferred).
            else:
                m1 *= min(3.0 * s1 / m1, 3.0 * s2 / m1, 1.0)

        # Now we can evaluate the Hermite spline
        result = (
            (m0 + m1 - 2.0 * s1) * t3 +
            (3.0 * s1 - 2.0 * m0 - m1) * t2 +
            m0 * t +
            p1
        )

        # As the spline is monotonic, all interpolated values should be confined between the endpoints.
        # Floating point arithmetic can cause this to be out of bounds on occasions.
        # If we are extrapolating (`t` is beyond the range), it doesn't really matter.
        return clamp(result, min(p1, p2), max(p1, p2)) if 0 <= t <= 1 else result


class BSplineInterpolator(_CubicInterpolator):
    """B-Spline Interpolator."""

    @staticmethod
    def interpolate(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
        """Calculate the new point using the provided values."""

        # Save some time calculating this once
        t2 = t ** 2
        t3 = t2 * t

        # Insert control points to algorithm
        return (
            ((1 - t) ** 3) * p0 +  # B0
            (3 * t3 - 6 * t2 + 4) * p1 +  # B1
            (-3 * t3 + 3 * t2 + 3 * t + 1) * p2 +  # B2
            t3 * p3  # B3
        ) / 6


@functools.lru_cache(maxsize=10)
def _matrix_141(n: int) -> MatrixT[float]:
    """Get matrix '1 4 1'."""

    m = [[0] * n for _ in range(n)]  # type: MatrixT[float]
    m[0][0:2] = M141[1:]
    m[-1][-2:] = M141[:-1]
    for x in range(n - 2):
        m[x + 1][x:x + 3] = M141
    return inv(m)


class NaturalBSplineInterpolator(BSplineInterpolator):
    """Natural B-Spline interpolator."""

    DEF_END_COND = 'natural'

    @staticmethod
    def naturalize(points: list[VectorT[float]]) -> None:
        """
        Given a set of B-spline control points in the Nth dimension, create naturalized interpolation control points.

        Using the color points as `S0...Sn`, calculate `B0...Bn`, such that interpolation will
        pass through `S0...Sn`.

        When given 2 data points, the operation will be returned as linear, so there is nothing to do.
        """

        n = len(points) - 2

        # Special case 3 data points
        if n == 1:
            points[1] = [
                (a * 6 - (b + c)) / 4 for a, b, c in zip(points[1], points[0], points[2])
            ]

        # Handle all other cases where n does not result in linear interpolation
        elif n > 1:
            # Create [1, 4, 1] matrix for size `n` set of control points
            m = _matrix_141(n)

            # Create C matrix from the data points
            c = []  # type: MatrixT[float]
            for r in range(1, n + 1):
                if r == 1:
                    c.append([a * 6 - b for a, b in zip(points[r], points[r - 1])])
                elif r == n:
                    c.append([a * 6 - b for a, b in zip(points[n], points[n + 1])])
                else:
                    c.append([a * 6 for a in points[r]])

            # Dot M^-1 and C to get B (control points)
            v = dot(m, c, dims=D2)
            for r in range(1, n + 1):
                points[r] = v[r - 1]

    @classmethod
    def preprocess(cls, points: list[VectorT[float]], end_cond: str | None = None, **kwargs: Any) -> None:
        """Apply any preprocessing points."""

        cls.naturalize(points)
        super(NaturalBSplineInterpolator, cls).preprocess(points, end_cond, **kwargs)


class SpragueInterpolator(Interpolator):
    """Sprague interpolator."""

    SPRAGUE_COEFFICIENTS = [
        [884, -1960, 3033, -2648, 1080, -180],
        [508, -540, 488, -367, 144, -24],
        [-24, 144, -367, 488, -540, 508],
        [-180, 1080, -2648, 3033, -1960, 884],
    ]

    @classmethod
    def preprocess(cls, points: list[VectorT[float]], **kwargs: Any) -> None:
        """Apply any preprocessing points."""

        if len(points) < 6:
            raise ValueError('Sprague interpolation requires at least 6 evenly spaced points.')
        # Create 2 points at the start and end of the data that will guide the interpolation
        # through the start and end points.
        p1, p2 = points[0:6], points[-6:]
        l = len(points[0])
        s0 = [0.0] * l
        s1 = [0.0] * l
        e0 = [0.0] * l
        e1 = [0.0] * l
        for i in range(l):
            # Each row of coefficients relates to one of the new points.
            # The top rows relate to the first two points we add to the start,
            # and we use the first 6 starting points as context. The last two
            # relate to the end points and use the last t points as context.
            s0[i], s1[i], e0[i], e1[i] = [
                vdot(row, [j[i] for j in (p1 if e < 2 else p2)]) / 209
                for e, row in enumerate(cls.SPRAGUE_COEFFICIENTS)
            ]
        points.insert(0, s0)
        points.insert(1, s1)
        points.append(e0)
        points.append(e1)

    def interpolate(self, p0: float, p1: float, p2: float, p3: float, p4: float, p5: float, t: float) -> float:
        """Interpolate with Sprague."""

        a0 = p2
        a1 = (2 * p0 - 16 * p1 + 16 * p3 + -2 * p4) / 24
        a2 = (-1 * p0 + 16 * p1 - 30 * p2 + 16 * p3 - 1 * p4) / 24
        a3 = (-9 * p0 + 39 * p1 - 70 * p2 + 66 * p3 - 33 * p4 + 7 * p5) / 24
        a4 = (13 * p0 - 64 * p1 + 126 * p2 - 124 * p3 + 61 * p4 - 12 * p5) / 24
        a5 = (-5 * p0 + 25 * p1 - 50 * p2 +  50 * p3 - 25 * p4 + 5 * p5) / 24

        t2 = t * t
        t3 = t2 * t
        t4 = t3 * t
        t5 = t4 * t

        return a0 + a1 * t + a2 * t2 + a3 * t3 + a4 * t4 + a5 * t5

    def run(self, i: int, t: float) -> VectorT[float]:
        """Begin interpolation."""

        coord = []
        for idx in range(self.num_coords):
            c = self.points[idx]
            coord.append(
                self.interpolate(
                    c[i],
                    c[i + 1],
                    c[i + 2],
                    c[i + 3],
                    c[i + 4],
                    c[i + 5],
                    t
                )
            )
        return coord


SPLINES = {
    'sprague': SpragueInterpolator,
    'natural': NaturalBSplineInterpolator,
    'bspline': BSplineInterpolator,
    'catrom': CatmullRomInterpolator,
    'monotone': MonotoneInterpolator,
    'linear': Interpolator
}  # type: dict[str, type[Interpolator]]


def interpolate(
    points: list[VectorT[float]] | VectorT[float],
    domain: VectorTLike[float] | None = None,
    method: str = 'linear',
    extrapolate: bool = True,
    **kwargs: Any
) -> Interpolator:
    """Generic interpolation method."""

    if points and isinstance(points[0], Sequence):
        return SPLINES[method](
            points[:],
            domain=domain,
            extrapolate=extrapolate,
            **kwargs
        )
    return SPLINES[method](
        cast('list[VectorT[float]]', [[p] for p in points]),
        domain=domain,
        extrapolate=extrapolate,
        **kwargs
    )


################################
# Matrix/linear algebra math
################################
def pretty(value: Number | ArrayTLike[Number], *, _depth: int = 0, shape: Shape | None = None) -> str:
    """Format the print output."""

    if shape is None:
        shape = _shape(value)

    nl = len(shape) - _depth - 1
    if isinstance(value, Sequence):
        seq = len(value) and isinstance(value[0], Sequence)
        values = [pretty(v, _depth=_depth + 1, shape=shape) for v in value]
        spacing = _depth + 1
        return '[{}]'.format((',{}{}'.format('\n' * nl, ' ' * spacing) if seq else ', ').join(values))

    return str(value)


def pprint(value: Number | ArrayTLike[Number]) -> None:
    """Print the matrix or value."""

    print(pretty(value))


def point_on_segment(
    a: VectorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    p: VectorTLike[StrictNumber],
    abs_tol: float = ATOL
) -> bool:
    """Point on line segment."""

    l = len(p)

    ab = [b[i] - a[i] for i in range(l)]
    ap = [p[i] - a[i] for i in range(l)]

    # Check if `ap` is parallel to `ab` (cross product is zero)
    cp = cross(ab, ap)
    if _any(abs(c) > abs_tol for c in cp):
        return False

    # Check if the point is between a and b
    for i in range(l):
        if abs(ab[i]) < abs_tol:
            continue
        t = ap[i] / ab[i]
        break

    # See if `ab` is a point and `p` is that point
    else:
        return _all(abs(i - j) < abs_tol for i, j in zip(a, p))

    return 0 <= t <= 1


def line_interesect(
    s1: VectorTLike[StrictNumber],
    e1: VectorTLike[StrictNumber],
    s2: VectorTLike[StrictNumber],
    e2: VectorTLike[StrictNumber],
    rel_tol: float = RTOL,
    abs_tol: float = ATOL
) -> VectorT[float] | None:
    """
    Find intersection of two lines.

    This was designed particularly for 3D intersection, but can be used for either 2D or 3D,
    but 2D line intersection could be calculated with less work using other methods if performance
    was of importance.

    3D lines rarely intersect, but often the shortest line between can be found.
    If the shortest line is has no length (a point) then it is an actual intersection.
    Our cases are constructed such that an intersection is expected, and a line is not sufficient.
    We can verify closeness of the points (to account for floating point errors) to verify that within
    some expected threshold, the two line points are essentially a point and an intersection is found.
    """

    # Line segment difference
    l1 = [a - b for a, b in zip(e1, s1)]
    l2 = [a - b for a, b in zip(e2, s2)]

    # Magnitude
    m1 = math.sqrt(sum(a ** 2 for a in l1))
    m2 = math.sqrt(sum(a ** 2 for a in l2))

    # One of the lines is a point.
    if m1 < abs_tol:
        return list(s1) if point_on_segment(e2, s2, s1, abs_tol=abs_tol) else None
    elif m2 < abs_tol:
        return list(s2) if point_on_segment(e1, s1, s2, abs_tol=abs_tol) else None

    # Unit vector
    u1 = [a / m1 for a in l1]
    u2 = [a / m2 for a in l2]
    # Direction projection
    u = vdot(u1, u2)
    if u == 1:  # pragma: no cover
        return None
    # Separation projection
    sp = [a - b for a, b in zip(s2, s1)]
    sp1 = vdot(sp, u1)
    sp2 = vdot(sp, u2)
    # Distance along lines
    d1 = (sp1 - u * sp2) / (1 - u * u)
    d2 = (sp2 - u * sp1) / (u * u - 1)
    # Calculate points of closest line
    p1 = [a + b for a, b in zip(s1, [x * d1 for x in u1])]
    p2 = [a + b for a, b in zip(s2, [x * d2 for x in u2])]
    # If points are close enough, assume intersect, otherwise raise error
    if not _all(math.isclose(i, j, rel_tol=rel_tol, abs_tol=abs_tol) for i, j in zip(p1, p2)):  # pragma: no cover
        return None
    return p1


def all(a: Number | ArrayTLike[Number], *, shape: Shape | None = None) -> bool:  # noqa: A001
    """Return true if all elements are "true"."""

    return _all(flatiter(a, shape=shape))


def any(a: Number | ArrayTLike[Number], *, shape: Shape | None = None) -> bool:  # noqa: A001
    """Return true if all elements are "true"."""

    return _any(flatiter(a, shape=shape))


def vdot(a: VectorTLike[StrictNumber], b: VectorTLike[StrictNumber]) -> StrictNumber:
    """Dot two vectors."""

    l = len(a)
    if l != len(b):
        raise ValueError(f'Vectors of size {l} and {len(b)} are not aligned')
    s = 0
    i = 0
    while i < l:
        s += a[i] * b[i]  # type: ignore[assignment]
        i += 1
    return s


def vdot_x3(a: VectorTLike[StrictNumber], b: VectorTLike[StrictNumber]) -> StrictNumber:
    """Dot two length 3 vectors."""

    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vcross(v1: VectorTLike[StrictNumber], v2: VectorTLike[StrictNumber]) -> Any:  # pragma: no cover
    """
    Cross two vectors.

    Takes vectors of either 2 or 3 dimensions. If 2 dimensions, will return the z component.
    To mix 2 and 3 vector components, please use `cross` instead which will pad 2 dimension
    vectors if the other is of 3 dimensions. `cross` has more overhead, so use `vcross` if
    you don't need broadcasting of any kind.
    """

    l1 = len(v1)
    if l1 != len(v2):
        raise ValueError(f'Incompatible dimensions of {l1} and {len(v2)} for cross product')

    if l1 == 2:
        return v1[0] * v2[1] - v1[1] * v2[0]
    elif l1 == 3:
        return [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v2[2] * v1[0],
            v1[0] * v2[1] - v1[1] * v2[0]
        ]
    else:
        raise ValueError(f'Expected vectors of shape (2,) or (3,) but got ({l1},) ({len(v2)},)')


@overload
def ascopy(a: VectorTLike[Number]) -> VectorT[Number]:
    ...


@overload
def ascopy(a: MatrixTLike[Number]) -> MatrixT[Number]:
    ...


@overload
def ascopy(a: TensorTLike[Number]) -> TensorT[Number]:
    ...


def ascopy(a: ArrayTLike[Number]) -> ArrayT[Number]:
    """Array copy."""

    return [(ascopy(i) if isinstance(i, Sequence) else i) for i in a]  # type: ignore[return-value]


@overload
def astype(a: VectorTLike[bool] | VectorTLike[int] | VectorTLike[float], dtype: type[Number]) -> VectorT[Number]:
    ...


@overload
def astype(a: MatrixTLike[bool] | MatrixTLike[int] | MatrixTLike[float], dtype: type[Number]) -> MatrixT[Number]:
    ...


@overload
def astype(a: TensorTLike[bool] | TensorTLike[int] | TensorTLike[float], dtype: type[Number]) -> TensorT[Number]:
    ...


def astype(a: ArrayTLike[bool] | ArrayTLike[int] | ArrayTLike[float], dtype: type[Number]) -> ArrayT[Number]:
    """Convert array to type."""

    return [(astype(i, dtype) if isinstance(i, Sequence) else dtype(i)) for i in a]  # type: ignore[return-value]


def _cross_pad(a: ArrayTLike[StrictNumber], s: ArrayShape) -> ArrayT[StrictNumber]:
    """Pad an array with 2-D vectors."""

    m = ascopy(a)

    # Initialize indexes so we can properly write our data
    total = math.prod(s[:-1])
    idx = [0] * (len(s) - 1)
    dtype = None

    for c in range(total):
        t = m  # type: Any
        for i in idx:
            t = t[i]

        if dtype is None:
            dtype = t[0].__class__
        t.append(dtype(0))

        if c < (total - 1):
            for x in range(len(s) - 1):
                if (idx[x] + 1) % s[x] == 0:
                    idx[x] = 0
                    x += 1
                else:
                    idx[x] += 1
                    break
    return m


def cross(a: ArrayTLike[StrictNumber], b: ArrayTLike[StrictNumber]) -> Any:
    """Vector cross product."""

    # Determine shape of arrays
    shape_a = shape(a)  # type: Shape
    shape_b = shape(b)  # type: Shape
    dims_a = len(shape_a)
    dims_b = len(shape_b)

    # Avoid crossing vectors of the wrong size or scalars
    if not shape_a or not shape_b or not (1 < shape_a[-1] < 4) or not (1 < shape_b[-1] < 4):
        raise ValueError('Values must contain vectors of dimensions 2 or 3')

    # Pad 2-D vectors
    if shape_a[-1] != shape_b[-1]:
        if shape_a[-1] == 2:
            a = _cross_pad(a, shape_a)
            shape_a = shape_a[:-1] + (3,)
        else:
            b = _cross_pad(b, shape_b)
            shape_b = shape_b[:-1] + (3,)

    # Cross two vectors
    if dims_a == 1 and dims_b == 1:
        return vcross(a, b)  # type: ignore[type-var]

    # Calculate cases of vector crossed either 2-D or N-D matrix and vice versa
    if dims_a == 1 or dims_b == 1:
        # Calculate target shape
        mdim = max(dims_a, dims_b)
        new_shape = list(_broadcast_shape([shape_a, shape_b], mdim))
        if mdim > 1 and new_shape[-1] == 2:
            new_shape.pop(-1)

        if dims_a == 2:
            # Cross a 2-D matrix and a vector
            result = [vcross(r, b) for r in a]  # type: Any # type: ignore[arg-type, type-var]

        elif dims_b == 2:
            # Cross a vector and a 2-D matrix
            result = [vcross(a, r) for r in b]  # type: ignore[arg-type, type-var]

        elif dims_a > 2:
            # Cross an N-D matrix and a vector
            m = new_shape[-2]
            rows = _extract_rows(a, shape_a)
            result = [[vcross(next(rows), b) for _ in range(m)] for _ in range(m)]  # type: ignore[type-var]

        else:
            # Cross a vector and an N-D matrix
            m = new_shape[-2]
            rows = _extract_rows(b, shape_b)
            result = [[vcross(a, next(rows)) for _ in range(m)] for _ in range(m)]  # type: ignore[type-var]

        return result

    # Cross an N-D and M-D matrix
    bcast = broadcast(a, b)
    a2 = []
    b2 = []
    count = 1
    size = bcast.shape[-1]

    # Adjust shape for the way cross outputs data
    new_shape = list(bcast.shape)
    mdim = max(dims_a, dims_b)
    if mdim > 1 and new_shape[-1] == 2:
        new_shape.pop(-1)
        s = tuple(new_shape)  # type: Shape
    else:
        s = tuple(new_shape)[:-1]

    result = []
    with ArrayBuilder(result, s) as build:
        for x, y in bcast:
            a2.append(x)
            b2.append(y)
            if count == size:
                next(build).append(vcross(a2, b2))
                a2 = []
                b2 = []
                count = 0
            count += 1

    return result


def _extract_rows(m: ArrayTLike[Number], s: ArrayShape) -> Iterator[VectorT[Number]]:
    """Extract row data from an array."""

    # Matrix or tensor
    for idx in ndindex(s[:-1]):
        t = m  # type: Any
        for i in idx:
            t = t[i]
        yield t


def _extract_cols(m: ArrayTLike[Number], s: ArrayShape) -> Iterator[VectorT[Number]]:
    """Extract column data from an array."""

    # Vector (nothing to do)
    if len(s) < 2:
        yield m  # type: ignore[misc]

    # M x N matrix
    else:
        for idx in ndindex(s[:-2]):
            t = m  # type: Any
            for i in idx:
                t = t[i]
            yield from [[r[c] for r in t] for c in range(s[-1])]


@overload
def dot(a: StrictNumber, b: StrictNumber, *, dims: DimHints = ...) -> StrictNumber:
    ...


@overload
def dot(a: StrictNumber, b: VectorTLike[StrictNumber], *, dims: DimHints = ...) -> VectorT[StrictNumber]:
    ...


@overload
def dot(a: VectorTLike[StrictNumber], b: StrictNumber, *, dims: DimHints = ...) -> VectorT[StrictNumber]:
    ...


@overload
def dot(a: StrictNumber, b: MatrixTLike[StrictNumber], *, dims: DimHints = ...) -> MatrixT[StrictNumber]:
    ...


@overload
def dot(a: MatrixTLike[StrictNumber], b: StrictNumber, *, dims: DimHints = ...) -> MatrixT[StrictNumber]:
    ...


@overload
def dot(a: StrictNumber, b: TensorTLike[StrictNumber], *, dims: DimHints = ...) -> TensorT[StrictNumber]:
    ...


@overload
def dot(a: TensorTLike[StrictNumber], b: StrictNumber, *, dims: DimHints = ...) -> TensorT[StrictNumber]:
    ...


@overload
def dot(a: VectorTLike[StrictNumber], b: VectorTLike[StrictNumber], *, dims: DimHints = ...) -> StrictNumber:
    ...


@overload
def dot(a: VectorTLike[StrictNumber], b: MatrixTLike[StrictNumber], *, dims: DimHints = ...) -> VectorT[StrictNumber]:
    ...


@overload
def dot(a: MatrixTLike[StrictNumber], b: VectorTLike[StrictNumber], *, dims: DimHints = ...) -> VectorT[StrictNumber]:
    ...


@overload
def dot(
    a: VectorTLike[StrictNumber],
    b: TensorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def dot(
    a: TensorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def dot(a: MatrixTLike[StrictNumber], b: MatrixTLike[StrictNumber], *, dims: DimHints = ...) -> MatrixT[StrictNumber]:
    ...


@overload
def dot(
    a: MatrixTLike[StrictNumber],
    b: TensorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def dot(
    a: TensorTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def dot(a: TensorTLike[StrictNumber], b: TensorTLike[StrictNumber], *, dims: DimHints = ...) -> TensorT[StrictNumber]:
    ...


def dot(
    a: StrictNumber | ArrayTLike[StrictNumber],
    b: StrictNumber | ArrayTLike[StrictNumber],
    *,
    dims: DimHints = DN,
) -> StrictNumber | ArrayT[StrictNumber]:
    """
    Perform dot product.

    Operations involving scalars will be the same as calling `multiply`.

    If you are doing matrix multiplication, equivalent to `@` in `numpy`,
    then you want to use `matmul` instead. Operations on arrays of dimension 2
    or less will act the same as `matmul`.
    """

    if dims[0] < 0 or dims[1] < 0 or dims[0] > 2 or dims[1] > 2:
        shape_a = shape(a)  # type: Shape
        shape_b = shape(b)  # type: Shape
        dims_a = len(shape_a)
        dims_b = len(shape_b)

        # Handle matrices of N-D and M-D size
        if dims_a and dims_b and (dims_a > 2 or dims_b > 2):
            result = []  # type: MatrixT[StrictNumber] | TensorT[StrictNumber]
            if dims_a == 1:
                # Dot product of vector and a M-D matrix
                with ArrayBuilder(result, shape_b[:-2] + shape_b[-1:]) as build:
                    b = cast("TensorT[StrictNumber]", b)
                    a = cast("VectorT[StrictNumber]", a)
                    for col in _extract_cols(b, shape_b):
                        next(build).append(vdot(a, col))
            elif dims_b == 1:
                # Dot product of vector and a M-D matrix
                with ArrayBuilder(result, shape_a[:-1]) as build:
                    a = cast("TensorT[StrictNumber]", a)
                    b = cast("VectorT[StrictNumber]", b)
                    for row in _extract_rows(a, shape_a):
                        next(build).append(vdot(row, b))
            else:
                # Dot product of N-D and M-D matrices
                # Resultant size: `dot(xy, yz) = xz` or `dot(nxy, myz) = nxmz`
                cols = [*_extract_cols(b, shape_b)]  # type: ignore[arg-type]
                n = shape_b[-1]  # type: ignore[misc]
                with ArrayBuilder(result, shape_a[:-1] + shape_b[:-2]) as build:
                    a = cast("TensorT[StrictNumber]", a)
                    b = cast("TensorT[StrictNumber]", b)
                    for row in _extract_rows(a, shape_a):
                        r = [sum(multiply(row, col, dims=D1)) for col in cols]  # type: ignore[arg-type,type-var]
                        start = 0
                        for _ in range(len(r) // n):
                            end = start + n
                            next(build).append(r[start:end])
                            start = end
            return result
    else:
        dims_a, dims_b = dims

    # Operations with scalars are the same as simply multiplying
    if not dims_a or not dims_b:
        return multiply(a, b, dims=(dims_a, dims_b))

    # Dot is identical to matrix multiply when dimensions are less than or equal to 2,
    return matmul(cast("ArrayT[StrictNumber]", a), cast("ArrayT[StrictNumber]", b), dims=(dims_a, dims_b))


@overload
def matmul(a: VectorTLike[StrictNumber], b: VectorTLike[StrictNumber], *, dims: DimHints = ...) -> StrictNumber:
    ...


@overload
def matmul(
    a: VectorTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def matmul(
    a: MatrixTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def matmul(
    a: VectorTLike[StrictNumber],
    b: TensorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def matmul(
    a: TensorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def matmul(
    a: MatrixTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


@overload
def matmul(
    a: MatrixTLike[StrictNumber],
    b: TensorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def matmul(
    a: TensorTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def matmul(
    a: TensorTLike[StrictNumber],
    b: TensorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber]:
    ...


def matmul(
    a: ArrayTLike[StrictNumber],
    b: ArrayTLike[StrictNumber],
    *,
    dims: DimHints = DN,
) -> StrictNumber | ArrayT[StrictNumber]:
    """
    Perform matrix multiplication of two arrays.

    Similar behavior as dot product, but this is limited to non-scalar values only. Additionally,
    the behavior of dimensions greater than 2 will be different. Stacks of matrices are broadcast
    together as if the matrices were elements, respecting the signature `(n,k),(k,m)->(n,m)`.
    This follows `numpy` behavior and is equivalent to the `@` operation.
    """

    if dims[0] < 0 or dims[1] < 0 or dims[0] > 2 or dims[1] > 2:
        shape_a = shape(a)  # type: ArrayShape
        shape_b = shape(b)  # type: ArrayShape
        dims_a = len(shape_a)
        dims_b = len(shape_b)

        # Handle matrices of N-D and M-D size
        if dims_a and dims_b and (dims_a > 2 or dims_b > 2):
            result = []  # type: MatrixT[StrictNumber] | TensorT[StrictNumber]
            if dims_a == 1:
                # Matrix multiply of vector and a M-D matrix
                with ArrayBuilder(result, shape_b[:-2] + shape_b[-1:]) as build:
                    b = cast("TensorT[StrictNumber]", b)
                    a = cast("VectorT[StrictNumber]", a)
                    for col in _extract_cols(b, shape_b):
                        next(build).append(vdot(a, col))
                return result
            elif dims_b == 1:
                # Matrix multiply of vector and a M-D matrix
                with ArrayBuilder(result, shape_a[:-1]) as build:
                    a = cast("TensorT[StrictNumber]", a)
                    b = cast("VectorT[StrictNumber]", b)
                    for row in _extract_rows(a, shape_a):
                         next(build).append(vdot(row, b))
                return result
            elif shape_a[-1] == shape_b[-2]:
                b = cast("TensorT[StrictNumber]", b)
                a = cast("TensorT[StrictNumber]", a)
                # Stacks of matrices are broadcast together as if the matrices were elements,
                # respecting the signature `(n,k),(k,m)->(n,m)`.
                common = _broadcast_shape([shape_a[:-2], shape_b[:-2]], max(dims_a, dims_b) - 2)
                shape_a = cast("TensorShape", common + shape_a[-2:])
                a2 = broadcast_to(a, shape_a)
                shape_b = cast("TensorShape", common + shape_b[-2:])
                b2 = broadcast_to(b, shape_b)
                with ArrayBuilder(result, common) as build:
                    for a1, b1 in it.zip_longest(_extract_rows(a2, shape_a[:-1]), _extract_rows(b2, shape_b[:-1])):  # type: ignore[misc]
                        next(build).append(matmul(a1, b1, dims=D2))
                return result
            raise ValueError(
                'Incompatible shapes in core dimensions (n?,k),(k,m?)->(n?,m?), {} != {}'.format(
                    shape_a[-1],
                    shape_b[-2]
                )
            )
    else:
        dims_a, dims_b = dims

    # Optimize to handle arrays <= 2-D
    if dims_a == 1:
        if dims_b == 1:
            # Matrix multiply of two vectors
            return vdot(a, b)  # type: ignore[return-value, type-var]
        elif dims_b == 2:
            # Matrix multiply of vector and a matrix
            return [vdot(a, col) for col in it.zip_longest(*b)]

    elif dims_a == 2:
        if dims_b == 1:
            # Matrix multiply of matrix and a vector
            return [vdot(row, b) for row in a]  # type: ignore[return-value, arg-type, type-var]
        if dims_b == 2:
            # Matrix multiply of two matrices
            cols = [*it.zip_longest(*b)]
            return [
                [vdot(row, col) for col in cols] for row in a  # type: ignore[arg-type]
            ]

    # Scalars are not allowed
    raise ValueError('Inputs require at least 1 dimension, scalars are not allowed')


@overload
def matmul_x3(a: VectorTLike[StrictNumber], b: VectorTLike[StrictNumber], *, dims: DimHints = ...) -> StrictNumber:
    ...


@overload
def matmul_x3(
    a: VectorTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def matmul_x3(
    a: MatrixTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def matmul_x3(
    a: MatrixTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


def matmul_x3(
    a: MatrixTLike[StrictNumber] | VectorTLike[StrictNumber],
    b: MatrixTLike[StrictNumber] | VectorTLike[StrictNumber],
    *,
    dims: DimHints = DN,
) -> StrictNumber | VectorT[StrictNumber] | MatrixT[StrictNumber]:
    """
    An optimized version of `matmul` that the total allowed dimensions to <= 2 and constrains dimensions lengths to 3.

    By limited to the total dimensions to < 2 and the dimension lengths of 3, loops are no longer required to handle
    an unknown number of dimensions or dimension lengths allowing for more optimized and faster performance at the
    cost of being able to handle any size arrays.

    For more flexibility with array sizes, use `matmul`.
    """

    dims_a = dims[0] if dims[0] >= 0 else len(shape(a))
    dims_b = dims[1] if dims[1] >= 0 else len(shape(b))

    # Optimize to handle arrays <= 2-D
    if dims_a == 1:
        if dims_b == 1:
            # Matrix multiply of two vectors
            return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]  # type: ignore[operator]
        elif dims_b == 2:
            # Matrix multiply of vector and a matrix
            return [
                a[0] * b[0][0] + a[1] * b[1][0] + a[2] * b[2][0],  # type: ignore[index, operator]
                a[0] * b[0][1] + a[1] * b[1][1] + a[2] * b[2][1],  # type: ignore[index, operator]
                a[0] * b[0][2] + a[1] * b[1][2] + a[2] * b[2][2]  # type: ignore[index, operator]
            ]

    elif dims_a == 2:
        if dims_b == 1:
            # Matrix multiply of matrix and a vector
            return [
                a[0][0] * b[0] + a[0][1] * b[1] + a[0][2] * b[2],  # type: ignore[index, operator]
                a[1][0] * b[0] + a[1][1] * b[1] + a[1][2] * b[2],  # type: ignore[index, operator]
                a[2][0] * b[0] + a[2][1] * b[1] + a[2][2] * b[2],  # type: ignore[index, operator]
            ]
        elif dims_b == 2:
            # Matrix and column vector
            if len(b[0]) == 1:  # type: ignore[arg-type]
                return [
                    [
                        a[0][0] * b[0][0] + a[0][1] * b[1][0] + a[0][2] * b[2][0],  # type: ignore[index]
                    ],
                    [
                        a[1][0] * b[0][0] + a[1][1] * b[1][0] + a[1][2] * b[2][0],  # type: ignore[index]
                    ],
                    [
                        a[2][0] * b[0][0] + a[2][1] * b[1][0] + a[2][2] * b[2][0],  # type: ignore[index]
                    ]
                ]
            # Two full matrices
            return [
                [
                    a[0][0] * b[0][0] + a[0][1] * b[1][0] + a[0][2] * b[2][0],  # type: ignore[index]
                    a[0][0] * b[0][1] + a[0][1] * b[1][1] + a[0][2] * b[2][1],  # type: ignore[index]
                    a[0][0] * b[0][2] + a[0][1] * b[1][2] + a[0][2] * b[2][2]  # type: ignore[index]
                ],
                [
                    a[1][0] * b[0][0] + a[1][1] * b[1][0] + a[1][2] * b[2][0],  # type: ignore[index]
                    a[1][0] * b[0][1] + a[1][1] * b[1][1] + a[1][2] * b[2][1],  # type: ignore[index]
                    a[1][0] * b[0][2] + a[1][1] * b[1][2] + a[1][2] * b[2][2]  # type: ignore[index]
                ],
                [
                    a[2][0] * b[0][0] + a[2][1] * b[1][0] + a[2][2] * b[2][0],  # type: ignore[index]
                    a[2][0] * b[0][1] + a[2][1] * b[1][1] + a[2][2] * b[2][1],  # type: ignore[index]
                    a[2][0] * b[0][2] + a[2][1] * b[1][2] + a[2][2] * b[2][2]  # type: ignore[index]
                ]
            ]

    # N > 2 dimensions are not allowed
    if dims_a > 2 or dims_b > 2:
        raise ValueError('Inputs cannot exceed 2 dimensions')

    # Scalars are not allowed
    raise ValueError('Inputs require at least 1 dimension, scalars are not allowed')


@overload
def dot_x3(a: StrictNumber, b: StrictNumber, *, dims: DimHints = ...) -> StrictNumber:
    ...


@overload
def dot_x3(a: StrictNumber, b: VectorTLike[StrictNumber], *, dims: DimHints = ...) -> VectorT[StrictNumber]:
    ...


@overload
def dot_x3(a: VectorTLike[StrictNumber], b: StrictNumber, *, dims: DimHints = ...) -> VectorT[StrictNumber]:
    ...


@overload
def dot_x3(a: StrictNumber, b: MatrixTLike[StrictNumber], *, dims: DimHints = ...) -> MatrixT[StrictNumber]:
    ...


@overload
def dot_x3(a: MatrixTLike[StrictNumber], b: StrictNumber, *, dims: DimHints = ...) -> MatrixT[StrictNumber]:
    ...


@overload
def dot_x3(a: VectorTLike[StrictNumber], b: VectorTLike[StrictNumber], *, dims: DimHints = ...) -> StrictNumber:
    ...


@overload
def dot_x3(
    a: VectorTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def dot_x3(
    a: MatrixTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def dot_x3(
    a: MatrixTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


def dot_x3(
    a: MatrixTLike[StrictNumber] | VectorTLike[StrictNumber] | StrictNumber,
    b: MatrixTLike[StrictNumber] | VectorTLike[StrictNumber] | StrictNumber,
    dims: DimHints = DN
) -> StrictNumber | VectorT[StrictNumber] | MatrixT[StrictNumber]:
    """
    An optimized version of `dot` that the total allowed dimensions to <= 2 and constrains dimensions lengths to 3.

    By limited to the total dimensions to < 2 and the dimension lengths of 3, loops are no longer required to handle
    an unknown number of dimensions or dimension lengths allowing for more optimized and faster performance at the
    cost of being able to handle any size arrays.

    For more flexibility with array sizes, use `dot`.
    """

    dims_a = dims[0] if dims[0] >= 0 else len(shape(a))
    dims_b = dims[1] if dims[1] >= 0 else len(shape(b))

    if not dims_a or not dims_b:
        return multiply_x3(a, b, dims=(dims_a, dims_b))

    return matmul_x3(
        cast('MatrixTLike[StrictNumber] | VectorTLike[StrictNumber]', a),
        cast('MatrixTLike[StrictNumber] | VectorTLike[StrictNumber]', b),
        dims=(dims_a, dims_b)
    )


def _matrix_chain_order(shapes: Sequence[ArrayShape]) -> MatrixT[int]:
    """
    Calculate chain order.

    Referenced the following sites:

    - https://en.wikipedia.org/wiki/Matrix_chain_multiplication
    - https://www.cs.cmu.edu/afs/cs/academic/class/15451-s04/www/Lectures/CRLS-DynamicProg.pdf

    This helped clarify `p` as that was not immediately clear:

    - https://www.geeksforgeeks.org/matrix-chain-multiplication-dp-8/

    We did adjust the looping. The algorithm originally called for looping from 2 - n,
    I can't see why though, so we've adjusted it to work from 1 - n.
    """

    n = len(shapes)
    m = full((n, n), 0)  # type: Any
    s = full((n, n), 0)  # type: MatrixT[int]
    p = [a[0] for a in shapes] + [shapes[-1][1]]

    for d in range(1, n):
        for i in range(n - d):
            j = i + d
            m[i][j] = math.inf
            for k in range(i, j):
                cost = m[i][k] + m[k + 1][j] + p[i] * p[k + 1] * p[j + 1]
                if cost < m[i][j]:
                    m[i][j] = cost
                    s[i][j] = k
    return s


def _multi_dot(arrays: Sequence[ArrayTLike[StrictNumber]], indexes: MatrixT[int], i: int, j: int) -> Any:
    """Recursively dot the matrices in the array."""

    if i != j:
        return dot(
            _multi_dot(arrays, indexes, i, int(indexes[i][j])),
            _multi_dot(arrays, indexes, int(indexes[i][j]) + 1, j),
            dims=D2
        )
    return arrays[i]


def multi_dot(arrays: Sequence[ArrayTLike[StrictNumber]]) -> Any:
    """
    Multi-dot.

    Dots matrices using the most efficient groupings to reduce operations.
    """

    is_scalar = False
    is_vector = False

    # Must have at lest two arrays
    count = len(arrays)
    if count == 1:
        raise ValueError('At least 2 arrays must be provided')

    # If there are only 2 arrays, just send them through normal dot
    elif count == 2:
        return dot(arrays[0], arrays[1])

    # Calculate the shapes
    shapes = [shape(a) for a in arrays]

    # We need the list mutable if we are going to update the entries
    _arrays = [*arrays] if not isinstance(arrays, list) else arrays  # type: Any

    # Row vector
    if len(shapes[0]) == 1:
        _arrays[0] = [arrays[0]]
        shapes[0] = (1,) + shapes[0]
        is_vector = True

    # Column vector
    if len(shapes[-1]) == 1:
        _arrays[-1] = transpose([_arrays[-1]])
        shapes[-1] = shapes[-1] + (1,)
        if is_vector:
            is_scalar = True
        else:
            is_vector = True

    # Make sure everything is a 2-D matrix as the next calculations only work for 2-D.
    if not _all(len(s) == 2 for s in shapes):
        raise ValueError('All arrays must be 2-D matrices')

    # No need to do the expensive and complicated chain order algorithm for only 3.
    # We can easily calculate three with less complexity and in less time. Anything
    # greater than three becomes a headache.
    if count == 3:
        pa = math.prod(shapes[0])
        pc = math.prod(shapes[2])
        cost1 = pa * shapes[2][0] + pc * shapes[0][0]
        cost2 = pc * shapes[0][1] + pa * shapes[2][1]  # type: ignore[misc]
        if cost1 < cost2:
            value = dot(dot(_arrays[0], _arrays[1], dims=D2), _arrays[2], dims=D2)  # type: Any
        else:
            value = dot(_arrays[0], dot(_arrays[1], _arrays[2], dims=D2), dims=D2)

    # Calculate the fastest ordering with dynamic programming using memoization
    s = _matrix_chain_order([shape(a) for a in _arrays])
    value = _multi_dot(_arrays, s, 0, count - 1)

    # `numpy` returns the shape differently depending on if there is a row and/or column vector
    if is_scalar:
        return value[0][0]
    elif is_vector:
        return ravel(value)
    else:
        return value


class _BroadcastTo(Generic[Number]):
    """
    Broadcast to a shape.

    By flattening the data, we are able to slice out the bits we need in the order we need
    and duplicate them to expand the matrix to fit the provided shape.

    We need 3 things to do this:
    - The original array.
    - The stage 1 array shape (with prepended 1s). This helps us calculate our loop iterations.
    - The new shape.
    """

    def __init__(self, array: ArrayTLike[Number] | Number, old: Shape, adjusted: Shape, new: Shape) -> None:
        """Initialize."""

        # Unravel the data as it will be quicker to slice the data in a flattened form
        # than iterating over the dimensions to replicate the data.
        self.data = ravel(array, shape=old)  # type: VectorT[Number]
        self.shape = new

        # Is the new shape actually different than the original?
        self.different = adjusted != new

        if 0 in new:
            # One of the common dimensions makes this result empty
            self.amount = self.length = self.expand = self.repeat = 0
        elif self.different:
            # Calculate the shape of the data.
            if len(adjusted) > 1:
                self.amount = math.prod(adjusted[:-1])
                self.length = adjusted[-1]
            else:
                # Vectors have to be handled a bit special as they only have 1-D
                self.amount = adjusted[-1]
                self.length = 1

            # Calculate how many times we should replicate data both horizontally and vertically
            # We need to flip them based on whether the original shape has an even or odd number of
            # dimensions.
            diff = [int(x / y) if y else y for x, y in zip(new, adjusted)]
            self.repeat = math.prod(diff[:-1]) if len(adjusted) > 1 else 1
            self.expand = diff[-1]
            if len(diff) > 1 and diff[-2] > 1:
                self.repeat, self.expand = self.expand, self.repeat
        else:
            # There is no modifications that need to be made on this array,
            # So we'll be chunking it without any cleverness.
            self.amount = math.prod(new)
            self.length = self.expand = self.repeat = 1

        self.reset()

    def reset(self) -> None:
        """Reset."""

        if not self.different:
            self._iter = iter(self.data)  # type: Iterator[Number]
        else:
            self._iter = it.chain.from_iterable(
                (
                    it.chain.from_iterable(
                        self.data[i * self.length:(i + 1) * self.length] * self.expand
                        for i in range(self.amount)
                    )
                )
                for _ in range(self.repeat)
            )

    def __next__(self) -> Number:
        """Next."""

        return next(self._iter)

    def __iter__(self) -> Iterator[Number]:
        """Return the broadcasted array, piece by piece."""

        return self


class _SimpleBroadcast(Generic[Number]):
    """
    Special broadcast of less than 2 arrays or 2 small dimension arrays that is faster than the generalized approach.

    A single array can have any dimensions, but two arrays must have dimensions less than 2.
    """

    def __init__(
        self,
        arrays: Sequence[ArrayTLike[Number] | Number],
        shapes: Sequence[Shape],
        new: Shape
    ) -> None:
        """Initialize."""

        self.empty = 0 in new

        total = len(arrays)
        if total == 0:
            self.a = []  # type: ArrayTLike[Number] | Number
            self.b = []  # type: ArrayTLike[Number] | Number
        elif total == 1:
            self.a, self.b = arrays[0], []
        else:
            self.a, self.b = arrays

        self.dims_a = len(shapes[0]) if self.a else 0
        self.shape_a = shapes[0] if self.a else ()
        self.dims_b = len(shapes[1]) if self.b else 0

        self.reset()

    def vector_broadcast(
        self,
        a: VectorTLike[Number],
        b: VectorTLike[Number]) -> Iterator[tuple[Number, ...]]:
        """Broadcast two vectors."""

        # Broadcast the vector
        if len(a) == 1:
            a = [a[0]] * len(b)
        elif len(b) == 1:
            b = [b[0]] * len(a)

        yield from it.zip_longest(a, b)

    def broadcast(self) -> Iterator[tuple[Number, ...]]:
        """Simple broadcast of a single array or two arrays with dimensions less than 2."""

        # One of the common dimensions makes this result empty
        if self.empty:
            return

        # Broadcast a single array case or empty set of arrays.
        if not self.b:
            if self.a:
                yield from ((i,) for i in flatiter(self.a, shape=self.shape_a))
            return

        a: Any = self.a
        b: Any = self.b
        dims_a: int = self.dims_a
        dims_b: int = self.dims_b

        # Inputs have matching dimensions.
        if dims_a == dims_b:
            if dims_a == 1:
                # Broadcast two vectors
                yield from self.vector_broadcast(a, b)
            elif dims_a == 2:
                # Broadcast two 2-D matrices
                la = len(a)
                lb = len(b)
                if la == 1 and lb != 1:
                    ra = a[0]
                    for rb in b:
                        yield from self.vector_broadcast(ra, rb)
                elif lb == 1 and la != 1:
                    rb = b[0]
                    for ra in a:
                        yield from self.vector_broadcast(ra, rb)
                else:
                    for ra, rb in it.zip_longest(a, b):
                        yield from self.vector_broadcast(ra, rb)
            else:
                yield a, b

        # Inputs containing a scalar on either side
        elif not dims_a or not dims_b:
            if dims_a == 1:
                # Apply math to a vector and number
                for i in a:
                    yield i, b
            elif dims_b == 1:
                # Apply math to a number and a vector
                for i in b:
                    yield a, i
            elif dims_a == 2:
                # Apply math to 2-D matrix and number
                for row in a:
                    for i in row:
                        yield i, b
            else:
                for row in b:
                    for i in row:
                        yield a, i

        # Inputs are at least 2-D dimensions or below on both sides
        elif dims_a == 1:
            # Broadcast a vector and 2-D matrix
            for row in b:
                yield from self.vector_broadcast(a, row)
        else:
            # Broadcast a 2-D matrix and a vector
            for row in a:
                yield from self.vector_broadcast(row, b)

    def reset(self) -> None:
        """Reset."""

        self._iter = self.broadcast()  # type: Iterator[tuple[Number, ...]]

    def __next__(self) -> tuple[Number, ...]:
        """Next."""

        # Get the next chunk of data
        return next(self._iter)

    def __iter__(self) -> Iterator[tuple[Number, ...]]:  # pragma: no cover
        """Iterate."""

        # Setup and return the iterator.
        return self


def _broadcast_shape(shapes: Sequence[Shape], max_dims: int, stage1_shapes: list[Shape] | None = None) -> Shape:
    """Find the common shape."""

    # Adjust array shapes by padding out with '1's until matches max dimensions
    if stage1_shapes is None:
        stage1_shapes = []

    for s in shapes:
        dims = len(s)
        stage1_shapes.append(((1,) * (max_dims - dims)) + s if dims < max_dims else s)

    # Determine a common shape, if possible
    s2 = []
    for dim in zip(*stage1_shapes):
        mx = 1
        for d in dim:
            if d != 1 and (d != mx and mx != 1):
                raise ValueError("Could not broadcast arrays as shapes are incompatible")
            if d != 1:
                mx = d
        s2.append(mx)
    return tuple(s2)


class Broadcast(Generic[Number]):
    """Broadcast."""

    def __init__(self, *arrays: ArrayTLike[Number] | Number) -> None:
        """Broadcast."""

        # Determine maximum dimensions
        shapes = []
        max_dims = 0
        for a in arrays:
            s = shape(a)
            dims = len(s)
            if dims > max_dims:
                max_dims = dims
            shapes.append(s)

        stage1_shapes = []  # type: list[Shape]
        common = _broadcast_shape(shapes, max_dims, stage1_shapes)

        # Create iterators to "broadcast to"
        total = len(arrays)
        self.simple = total < 2 or (total == 2 and len(common) <= 2)
        if self.simple:
            self.simple_iter = _SimpleBroadcast(arrays, shapes, common)  # type: _SimpleBroadcast[Number]
        else:
            self.iters = [_BroadcastTo(a, s, s1, common) for a, s, s1 in zip(arrays, shapes, stage1_shapes)]  # type: list[_BroadcastTo[Number]]

        # I don't think this is done the same way as `numpy`.
        # But shouldn't matter for what we do.
        self.shape = common
        self.ndims = max_dims
        self.size = math.prod(common)
        self._init()

    def _init(self) -> None:
        """Setup main iterator."""

        self._iter = self.simple_iter if self.simple else it.zip_longest(*self.iters)  # type: Iterator[tuple[Number, ...]]

    def reset(self) -> None:
        """Reset iterator."""

        # Reset all the child iterators.
        if self.simple:
            self.simple_iter.reset()
        else:
            for i in self.iters:
                i.reset()
        self._init()

    def __next__(self) -> tuple[Number, ...]:
        """Next."""

        # Get the next chunk of data
        return next(self._iter)

    def __iter__(self) -> Broadcast[Number]:
        """Iterate."""

        # Setup and return the iterator.
        return self


def broadcast(*arrays: ArrayTLike[Number] | Number) -> Broadcast[Number]:
    """Broadcast."""

    return Broadcast(*arrays)


@overload
def broadcast_to(a: ArrayTLike[Number] | Number, s: EmptyShape) -> Number:
    ...


@overload
def broadcast_to(a: ArrayTLike[Number] | Number, s: int | VectorShape) -> VectorT[Number]:
    ...


@overload
def broadcast_to(a: ArrayTLike[Number] | Number, s: MatrixShape) -> MatrixT[Number]:
    ...


@overload
def broadcast_to(a: ArrayTLike[Number] | Number, s: TensorShape) -> TensorT[Number]:
    ...


def broadcast_to(a: ArrayTLike[Number] | Number, s: int | Shape) -> Number | ArrayT[Number]:
    """Broadcast array to a shape."""

    _s = (s,) if not isinstance(s, Sequence) else tuple(s)

    s_orig = shape(a)
    ndim_orig = len(s_orig)
    ndim_target = len(_s)
    if ndim_orig > ndim_target:
        raise ValueError(f"Cannot broadcast {s_orig} to {_s}")

    if not ndim_target:
        return a  # type: ignore[return-value]

    s1 = list(s_orig)
    if ndim_orig < ndim_target:
        s1 = ([1] * (ndim_target - ndim_orig)) + s1

    for d1, d2 in zip(s1, _s):
        if d1 != d2 and (d1 != 1 or d1 > d2):
            raise ValueError(f"Cannot broadcast {s_orig} to {_s}")

    bcast = _BroadcastTo(a, s_orig, tuple(s1), tuple(_s))
    if len(_s) > 1:
        result = [] # type: ArrayT[Number]
        with ArrayBuilder(result, _s) as build:
            for data in bcast:
                next(build).append(data)
        return result

    return list(bcast)


class vectorize:
    """
    Vectorize a call.

    We do not currently support signatures, caching, and none of our functions allow specifying output
    types. All are assumed floats. Specialized methods will be far more performant than using vectorize,
    but vectorize can be quick to use as far as convenience is concerned.

    There is no optimization for small matrices or matrices that are already the same size. This
    assumes worst case: N x M matrices of unknown quantity.

    Inputs and outputs are currently assumed to be scalars. We do not detect alternate sizes nor
    do we allow specifying function signatures to change it at this time.
    """

    def __init__(
        self,
        pyfunc: Callable[..., Any],
        doc: str | None = None,
        excluded: Sequence[str | int] | None = None
    ) -> None:
        """Initialize."""

        # Save the function and the exclude list
        self.func = pyfunc
        self.excluded = set() if excluded is None else set(excluded)

        # Setup function name and docstring
        self.__name__ = self.func.__name__
        self.__doc__ = self.func.__doc__ if doc is None else doc

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the function after once arguments are vectorized."""

        # No arguments to process, just call the function.
        if not args and not kwargs:
            return self.func()

        # Determine which keys and indexes we want to vectorize
        indexes = [a for a in range(len(args)) if a not in self.excluded]
        keys = [k for k in kwargs if k not in self.excluded]
        size = len(indexes)

        # Cast to a list so we can update the input arguments with vectorized inputs
        inputs = [*args]

        # Gather all the input values we need to vectorize so we can broadcast them together
        vinputs = [inputs[i] for i in indexes] + [kwargs[k] for k in keys]

        if vinputs:
            # We need to broadcast together the inputs for vectorization.
            # Once vectorized, use the wrapper function to replace each argument
            # with the vectorized iteration while building up the array.
            bcast = broadcast(*vinputs)
            new_shape = bcast.shape
            # Build up the matrix
            m = []  # type: ArrayT[float]
            with ArrayBuilder(m, new_shape) as build:
                for vargs in bcast:
                    # Update arguments with vectorized arguments
                    for e, i in enumerate(indexes):
                        inputs[i] = vargs[e]

                    # Update keyword arguments with vectorized keyword argument
                    kwargs.update(zip(keys, vargs[size:]))

                    # Create the final dimension, writing all the data
                    next(build).append(self.func(*inputs, **kwargs) if kwargs else self.func(*inputs))
            return m

        # Nothing to vectorize, just run the function with the arguments
        return self.func(*inputs, **kwargs) if kwargs else self.func(*inputs)


class _vectorize1:
    """
    An optimized version of vectorize that is hard coded to broadcast only the first input.

    This is faster than `vectorize` as it skips a lot of generalization code that allows a user
    to specify specific parameters to broadcast. Additionally, users can specify `dims` allowing
    us to skip analyzing the array to determine the size allowing for additional speedup.

    For more flexibility, use `vectorize` which allows arbitrary vectorization of any and
    all inputs at the cost of speed.
    """

    def __init__(self, pyfunc: Callable[..., Any], doc: str | None = None):
        """Initialize."""

        self.func = pyfunc

        # Setup function name and docstring
        self.__name__ = self.func.__name__
        self.__doc__ = self.func.__doc__ if doc is None else doc

    def __call__(
        self,
        a: ArrayTLike[Number] | Number,
        dims: DimHints = DN,
        **kwargs: Any
    ) -> Any:
        """Call the vectorized function."""

        dims_a = dims[0] if dims[0] >= 0 else len(shape(a))
        func = (lambda p1, kw=kwargs: self.func(p1, **kw)) if kwargs else self.func  # type: Callable[..., Any]

        # Fast paths for scalar, vectors, and 2D matrices
        # Scalar
        if dims_a == 0:
            return func(a)
        # Vector
        elif dims_a == 1:
            return [func(i) for i in a]  # type: ignore[union-attr]
        # 2D matrix
        elif dims_a == 2:
            return [[func(c) for c in r] for r in a]  # type: ignore[union-attr]

        # Unknown size or larger than 2D (slow)
        m = []  # type: ArrayT[float]
        s = shape(a)
        with ArrayBuilder(m, s) as build:
            for f in flatiter(a, shape=s):
                next(build).append(func(f))
        return m


class _vectorize2:
    """
    An optimized version of vectorize that is hard coded to broadcast only the first two inputs.

    This is faster than `vectorize` as it skips a lot of generalization code that allows a user
    to specify specific parameters to broadcast. Additionally, users can specify `dims` allowing
    us to skip analyzing the array to determine the size allowing for additional speedup.

    For more flexibility, use `vectorize` which allows arbitrary vectorization of any and
    all inputs at the cost of speed.
    """

    def __init__(self, pyfunc: Callable[..., Any], doc: str | None = None):
        """Initialize."""

        self.func = pyfunc

        # Setup function name and docstring
        self.__name__ = self.func.__name__
        self.__doc__ = self.func.__doc__ if doc is None else doc

    def _vector_apply(self, a: VectorTLike[float], b: VectorTLike[float], func: Callable[..., Any]) -> Any:
        """Apply a function to two vectors."""

        # Broadcast the vector
        if len(a) == 1:
            a = [a[0]] * len(b)
        elif len(b) == 1:
            b = [b[0]] * len(a)

        return [func(x, y) for x, y in it.zip_longest(a, b)]

    def __call__(
        self,
        a: ArrayTLike[Number] | Number,
        b: ArrayTLike[Number] | Number,
        dims: DimHints = DN,
        **kwargs: Any
    ) -> Any:
        """Call the vectorized function."""

        func = (lambda p1, p2, kw=kwargs: self.func(p1, p2, **kw)) if kwargs else self.func  # type: Callable[..., Any]

        if dims[0] < 0 or dims[1] < 0 or dims[0] > 2 or dims[1] > 2:
            shape_a = shape(a)
            shape_b = shape(b)
            dims_a = len(shape_a)
            dims_b = len(shape_b)

            # Handle matrices of N-D and M-D size
            if dims_a > 2 or dims_b > 2:
                m = []  # type: ArrayT[float]
                # Apply math to two N-D matrices
                if dims_a == dims_b:
                    empty = (not shape_a or 0 in shape_a) and (not shape_b or 0 in shape_b)
                    if not empty and math.prod(shape_a) != math.prod(shape_b):  # pragma: no cover
                        raise ValueError(f'Shape {shape_a} does not match the data total of {shape_b}')
                    with ArrayBuilder(m, shape_a) as build:
                        for x, y in zip(flatiter(a, shape=shape_a), flatiter(b, shape=shape_b)):
                            next(build).append(func(x, y))

                elif not dims_a or not dims_b:
                    # Apply math to a number and an N-D matrix
                    if not dims_a:
                        with ArrayBuilder(m, shape_b) as build:
                            for x in flatiter(b, shape=shape_b):
                                next(build).append(func(a, x))

                    # Apply math to an N-D matrix and a number
                    else:
                        with ArrayBuilder(m, shape_a) as build:
                            for x in flatiter(a, shape=shape_a):
                                next(build).append(func(x, b))

                # Apply math to an N-D matrix and an M-D matrix by broadcasting to a common shape.
                else:
                    bcast = broadcast(a, b)
                    with ArrayBuilder(m, bcast.shape) as build:
                        for x, y in bcast:
                            next(build).append(func(x, y))

                return m
        else:
            dims_a, dims_b = dims

        # Inputs are of equal size and shape
        if dims_a == dims_b:
            if dims_a == 1:
                # Apply math to two vectors
                return self._vector_apply(a, b, func)  # type: ignore[arg-type]
            elif dims_a == 2:
                # Apply math to two 2-D matrices
                la = len(a)  # type: ignore[arg-type]
                lb = len(b)  # type: ignore[arg-type]
                if la == 1 and lb != 1:
                    ra = a[0]  # type: ignore[index]
                    return [self._vector_apply(ra, rb, func) for rb in b]  # type: ignore[arg-type, union-attr]
                elif lb == 1 and la != 1:
                    rb = b[0]  # type: ignore[index]
                    return [self._vector_apply(ra, rb, func) for ra in a]  # type: ignore[arg-type, union-attr]
                return [
                    self._vector_apply(ra, rb, func) for ra, rb in it.zip_longest(a, b)  # type: ignore[arg-type]
                ]
            # Apply math to two scalars
            return func(a, b)

        # Inputs containing a scalar on either side
        elif not dims_a or not dims_b:
            if dims_a == 1:
                # Apply math to a vector and number
                return [func(i, b) for i in a]  # type: ignore[union-attr]
            elif dims_b == 1:
                # Apply math to a number and a vector
                return [func(a, i) for i in b]  # type: ignore[union-attr]
            elif dims_a == 2:
                # Apply math to 2-D matrix and number
                return [[func(i, b) for i in row] for row in a]  # type: ignore[union-attr]
            # Apply math to a number and a matrix
            return [[func(a, i) for i in row] for row in b]  # type: ignore[union-attr]

        # Inputs are at least 2-D dimensions or below on both sides
        if dims_a == 1:
            # Apply math to vector and 2-D matrix
            return [self._vector_apply(a, row, func) for row in b]  # type: ignore[arg-type, union-attr]
        # Apply math to 2-D matrix and a vector
        return [self._vector_apply(row, b, func) for row in a]  # type: ignore[arg-type, union-attr]


class _vectorize1_x3:
    """
    A further optimized version of `_vectorize1` that limits arrays to dimensions of <= 2 and dimension to lengths of 3.

    Like `_vectorize1`, this limits the broadcasting to the first parameter and is faster than `vectorize` as it skips
    a lot of generalization code that allows a user to specify specific parameters to broadcast. Additionally, users
    can specify `dims` allowing us to skip analyzing the array to determine the size allowing for additional speedup.
    Lastly, dimensions are limited to a total less than 2 and the length of dimensions is limited to 3 which allows us
    to avoid looping since the dimension length is always the same.

    For more flexibility, use `vectorize` which allows arbitrary vectorization of any and
    all inputs at the cost of speed.
    """

    def __init__(self, pyfunc: Callable[..., Any], doc: str | None = None):
        """Initialize."""

        self.func = pyfunc

        # Setup function name and docstring
        self.__name__ = self.func.__name__
        self.__doc__ = self.func.__doc__ if doc is None else doc

    def __call__(
        self,
        a: MatrixTLike[Number] | VectorTLike[Number] | Number,
        dims: DimHints = DN,
        **kwargs: Any
    ) -> Any:
        """Call the vectorized function."""

        dims_a = dims[0] if dims[0] >= 0 else len(shape(a))

        if not (0 <= dims_a <= 2):
            raise ValueError('Inputs cannot exceed 2 dimensions')

        func = (lambda p1, kw=kwargs: self.func(p1, **kw)) if kwargs else self.func  # type: Callable[..., Any]

        # Fast paths for scalar, vectors, and 2D matrices
        # Scalar
        if dims_a == 0:
            return func(a)
        # Vector
        elif dims_a == 1:
            return [func(a[0]), func(a[1]), func(a[2])]  # type: ignore[index]

        # Column vector
        if len(a[0]) == 1:  # type: ignore[arg-type, index]
            return [
                [func(a[0][0])],  # type: ignore[index]
                [func(a[1][0])],  # type: ignore[index]
                [func(a[2][0])]  # type: ignore[index]
            ]

        # 2D matrix
        return [
            [func(a[0][0]), func(a[0][1]), func(a[0][2])],  # type: ignore[index]
            [func(a[1][0]), func(a[1][1]), func(a[1][2])],  # type: ignore[index]
            [func(a[2][0]), func(a[2][1]), func(a[2][2])]  # type: ignore[index]
        ]


class _vectorize2_x3:
    """
    A further optimized version of `_vectorize2` that limits arrays to dimensions of <= 2 and dimension to lengths of 3.

    Like `_vectorize2`, this limits the broadcasting to the first two parameter and is faster than `vectorize` as it
    skips a lot of generalization code that allows a user to specify specific parameters to broadcast. Additionally,
    users can specify `dims` allowing us to skip analyzing the array to determine the size allowing for additional
    speedup. Lastly, dimensions are limited to a total less than 2 and the length of dimensions is limited to 3 which
    allows us to avoid looping since the dimension length is always the same.

    For more flexibility, use `vectorize` which allows arbitrary vectorization of any and
    all inputs at the cost of speed.
    """

    def __init__(self, pyfunc: Callable[..., Any], doc: str | None = None):
        """Initialize."""

        self.func = pyfunc

        # Setup function name and docstring
        self.__name__ = self.func.__name__
        self.__doc__ = self.func.__doc__ if doc is None else doc

    def __call__(
        self,
        a: MatrixTLike[Number] | VectorTLike[Number] | Number,
        b: MatrixTLike[Number] | VectorTLike[Number] | Number,
        dims: DimHints = DN,
        **kwargs: Any
    ) -> Any:
        """Call the vectorized function."""

        dims_a = dims[0] if dims[0] >= 0 else len(shape(a))
        dims_b = dims[1] if dims[1] >= 0 else len(shape(b))

        func = (lambda a, b, kw=kwargs: self.func(a, b, **kw)) if kwargs else self.func  # type: Callable[..., float]

        if dims_a > 2 or dims_b > 2:
            raise ValueError('Inputs cannot exceed 2 dimensions')

        # Inputs are of equal size and shape
        if dims_a == dims_b:
            if dims_a == 1:
                # Apply math to two vectors
                return [func(a[0], b[0]), func(a[1], b[1]), func(a[2], b[2])]  # type: ignore[index]
            elif dims_a == 2:
                l1 = len(a[0])  # type: ignore[arg-type, index]
                l2 = len(b[0])  # type: ignore[arg-type, index]
                if l1 != l2:
                    if l2 == 1:
                        # Column vector in first position
                        return [
                            [func(a[0][0], b[0][0]), func(a[0][1], b[0][0]), func(a[0][2], b[0][0])],  # type: ignore[index]
                            [func(a[1][0], b[1][0]), func(a[1][1], b[1][0]), func(a[1][2], b[1][0])],  # type: ignore[index]
                            [func(a[2][0], b[2][0]), func(a[2][1], b[2][0]), func(a[2][2], b[2][0])],  # type: ignore[index]
                        ]
                    elif l1 == 1:
                        # Column vector in second position
                        return [
                            [func(a[0][0], b[0][0]), func(a[0][0], b[0][1]), func(a[0][0], b[0][2])],  # type: ignore[index]
                            [func(a[1][0], b[1][0]), func(a[1][0], b[1][1]), func(a[1][0], b[1][2])],  # type: ignore[index]
                            [func(a[2][0], b[2][0]), func(a[2][0], b[2][1]), func(a[2][0], b[2][2])],  # type: ignore[index]
                        ]
                    raise ValueError(f'Vectors of size {l1} and {l2} are not aligned')
                elif l1 == 1:
                    # 2 column vectors
                    return [
                        [func(a[0][0], b[0][0])],  # type: ignore[index]
                        [func(a[1][0], b[1][0])],  # type: ignore[index]
                        [func(a[2][0], b[2][0])],  # type: ignore[index]
                    ]
                # Apply math to two 2-D matrices
                return [
                    [func(a[0][0], b[0][0]), func(a[0][1], b[0][1]), func(a[0][2], b[0][2])],  # type: ignore[index]
                    [func(a[1][0], b[1][0]), func(a[1][1], b[1][1]), func(a[1][2], b[1][2])],  # type: ignore[index]
                    [func(a[2][0], b[2][0]), func(a[2][1], b[2][1]), func(a[2][2], b[2][2])],  # type: ignore[index]
                ]
            # Apply math to two scalars
            return func(a, b)

        # Inputs containing a scalar on either side
        elif not dims_a or not dims_b:
            if dims_a == 1:
                # Apply math to a vector and number
                return [func(a[0], b), func(a[1], b), func(a[2], b)]  # type: ignore[index]
            elif dims_b == 1:
                # Apply math to a number and a vector
                return [func(a, b[0]), func(a, b[1]), func(a, b[2])]  # type: ignore[index]
            elif dims_a == 2:
                # Apply math to 2-D matrix and number
                return [
                    [func(a[0][0], b), func(a[0][1], b), func(a[0][2], b)],  # type: ignore[index]
                    [func(a[1][0], b), func(a[1][1], b), func(a[1][2], b)],  # type: ignore[index]
                    [func(a[2][0], b), func(a[2][1], b), func(a[2][2], b)]  # type: ignore[index]
                ]
            # Apply math to a number and a matrix
            return [
                [func(a, b[0][0]), func(a, b[0][1]), func(a, b[0][2])],  # type: ignore[index]
                [func(a, b[1][0]), func(a, b[1][1]), func(a, b[1][2])],  # type: ignore[index]
                [func(a, b[2][0]), func(a, b[2][1]), func(a, b[2][2])]  # type: ignore[index]
            ]

        # Inputs are at least 2-D dimensions or below on both sides
        if dims_a == 1:
            # Apply math to vector and 2-D matrix
            return [
                [func(a[0], b[0][0]), func(a[1], b[0][1]), func(a[2], b[0][2])],  # type: ignore[index]
                [func(a[0], b[1][0]), func(a[1], b[1][1]), func(a[2], b[1][2])],  # type: ignore[index]
                [func(a[0], b[2][0]), func(a[1], b[2][1]), func(a[2], b[2][2])]  # type: ignore[index]
            ]
        # Apply math to 2-D matrix and a vector
        return [
            [func(a[0][0], b[0]), func(a[0][1], b[1]), func(a[0][2], b[2])],  # type: ignore[index]
            [func(a[1][0], b[0]), func(a[1][1], b[1]), func(a[1][2], b[2])],  # type: ignore[index]
            [func(a[2][0], b[0]), func(a[2][1], b[1]), func(a[2][2], b[2])]  # type: ignore[index]
        ]


def vectorize2(
    pyfunc: Callable[..., Any],
    doc: str | None = None,
    params: int = 2,
    only_x3: bool = False
) -> Callable[..., Any]:
    """
    A more limited but faster version of `vectorize` that speed up performance at the cost of flexibility.

    1. Broadcasted parameters are limited to the first 1 or 2 parameters via the `params` option (default 2).
    2. Further limits the expectation of the array in the first 1 or 2 parameters to dimension lengths of 3.
       Additionally, the total number of dimensions cannot exceed 2. `only_x3` enables this behavior and will
       provide the most speed but provides the most limited environment for operations.

    The limitations above allows the avoidance of additional generalized code that can slow the operation down.

    For more flexibility, use `vectorize` which allows arbitrary vectorization of any and
    all inputs at the cost of speed.
    """

    if params == 2:
        return (_vectorize2_x3 if only_x3 else _vectorize2)(pyfunc, doc)
    elif params == 1:
        return (_vectorize1_x3 if only_x3 else _vectorize1)(pyfunc, doc)
    raise ValueError("'vectorize2' does not support dimensions greater than 2 or less than 1")


@overload
def linspace(start: StrictNumber, stop: StrictNumber, num: int = ..., endpoint: bool = ...) -> VectorT[float]:
    ...


@overload
def linspace(
    start: VectorTLike[StrictNumber],
    stop: VectorTLike[StrictNumber] | StrictNumber,
    num: int = ...,
    endpoint: bool = ...
) -> MatrixT[float]:
    ...


@overload
def linspace(
    start: VectorTLike[StrictNumber] | StrictNumber,
    stop: VectorTLike[StrictNumber],
    num: int = ...,
    endpoint: bool = ...
) -> MatrixT[float]:
    ...


@overload
def linspace(
    start: MatrixTLike[StrictNumber],
    stop: ArrayTLike[StrictNumber],
    num: int = ...,
    endpoint: bool = ...
) -> TensorT[float]:
    ...


@overload
def linspace(
    start: ArrayTLike[StrictNumber],
    stop: MatrixTLike[StrictNumber],
    num: int = ...,
    endpoint: bool = ...
) -> TensorT[float]:
    ...


def linspace(
    start: ArrayTLike[StrictNumber] | StrictNumber,
    stop: ArrayTLike[StrictNumber] | StrictNumber,
    num: int = 50,
    endpoint: bool = True
) -> ArrayT[float]:
    """Create a series of points in a linear space."""

    if num < 0:
        raise ValueError('Cannot return a negative amount of values')

    # Return empty results over all the inputs for a request of 0
    if num == 0:
        return full(broadcast(start, stop).shape + (0,), [])  # type: ignore[type-var, arg-type]

    # Calculate denominator
    d = float(num - 1 if endpoint else num)

    s1 = shape(start)
    s2 = shape(stop)
    dim1 = len(s1)
    dim2 = len(s2)

    # Scalar case (faster)
    if dim1 == 0 and dim2 == 0:
        return [lerp(float(start), float(stop), r / d if d != 0 else 0.0) for r in range(num)]  # type: ignore[arg-type]

    # Vector case
    if dim1 <= 1 and dim2 <= 1:
        # Broadcast scalars to match vectors
        if dim1 == 0:
            begin = [cast('StrictNumber', start)] * s2[0]  # type: VectorT[StrictNumber]  # type: ignore[misc]
            end = cast('VectorT[StrictNumber]', stop)  # type: VectorT[StrictNumber]
            s1 = s2
        elif dim2 == 0:
            begin = cast('VectorT[StrictNumber]', start)
            end = [cast('StrictNumber', stop)] * s1[0]  # type: ignore[misc]
            s2 = s1
        else:
            begin = cast('VectorT[StrictNumber]', start)
            end = cast('VectorT[StrictNumber]', stop)

        # Broadcast length 1 vectors to match other vector
        if s1[0] != s2[0]:  # type: ignore[misc]
            if s1[0] == 1:  # type: ignore[misc]
                begin = begin * s2[0]  # type: ignore[misc]
            elif s2[0] == 1:  # type: ignore[misc]
                end = end * s1[0]  # type: ignore[misc]
            else:
                raise ValueError(f'Cannot broadcast start ({s1}) and stop ({s2})')

        # Apply linear interpolation steps across the vectors
        values = [*zip(begin, end)]
        m1 = []  # type: MatrixT[float]
        for r in range(num):
            m1.append([])
            for a, b in values:
                m1[-1].append(lerp(float(a), float(b), r / d if d != 0 else 0.0))
        return m1

    # To apply over N x M inputs, apply the steps over the broadcasted results (slower)
    m = []  # type: TensorT[float]
    bcast = broadcast(start, stop)
    new_shape = (num,) + bcast.shape
    with ArrayBuilder(m, new_shape) as build:
        for r in range(num):
            bcast.reset()
            for a2, b2 in bcast:
                next(build).append(lerp(float(a2), float(b2), r / d if d != 0 else 0.0))
    return m


def _isclose(a: StrictNumber, b: StrictNumber, *, equal_nan: bool = False, **kwargs: Any) -> bool:
    """Check if values are close."""

    close = math.isclose(a, b, **kwargs) if kwargs else math.isclose(a, b)
    return (math.isnan(a) and math.isnan(b)) if not close and equal_nan else close


@overload  # type: ignore[no-overload-impl]
def isclose(
    a: StrictNumber,
    b: StrictNumber,
    *,
    dims: DimHints = ...,
    **kwargs: Any
) -> bool:
    ...


@overload
def isclose(
    a: VectorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...,
    **kwargs: Any
) -> VectorT[bool]:
    ...


@overload
def isclose(
    a: MatrixTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...,
    **kwargs: Any
) -> MatrixT[bool]:
    ...


@overload
def isclose(
    a: TensorTLike[StrictNumber],
    b: TensorTLike[StrictNumber],
    *,
    dims: DimHints = ...,
    **kwargs: Any
) -> TensorT[bool]:
    ...


@overload
def isclose(
    a: ArrayTLike[StrictNumber],
    b: ArrayTLike[StrictNumber],
    *,
    dims: DimHints = ...,
    **kwargs: Any
) -> ArrayT[bool]:
    ...


isclose = vectorize2(_isclose, doc="Test if a value or value(s) in an array are close to another value(s).")


@overload  # type: ignore[no-overload-impl]
def isnan(a: StrictNumber, *, dims: DimHints = ..., **kwargs: Any) -> bool:
    ...


@overload
def isnan(a: VectorTLike[StrictNumber], *, dims: DimHints = ..., **kwargs: Any) -> VectorT[bool]:
    ...


@overload
def isnan(a: MatrixTLike[StrictNumber], *, dims: DimHints = ..., **kwargs: Any) -> MatrixT[bool]:
    ...


@overload
def isnan(a: TensorTLike[StrictNumber], *, dims: DimHints = ..., **kwargs: Any) -> TensorT[bool]:
    ...


@overload
def isnan(a: ArrayTLike[StrictNumber], *, dims: DimHints = ..., **kwargs: Any) -> ArrayT[bool]:
    ...


isnan = vectorize2(math.isnan, doc="Test if a value or values in an array are NaN.", params=1)


@overload  # type: ignore[no-overload-impl]
def sign(a: StrictNumber, *, dims: DimHints = ..., **kwargs: Any) -> StrictNumber:
    ...


@overload
def sign(a: VectorTLike[StrictNumber], *, dims: DimHints = ..., **kwargs: Any) -> VectorT[StrictNumber]:
    ...


@overload
def sign(a: MatrixTLike[StrictNumber], *, dims: DimHints = ..., **kwargs: Any) -> MatrixT[StrictNumber]:
    ...


@overload
def sign(a: TensorTLike[StrictNumber], *, dims: DimHints = ..., **kwargs: Any) -> TensorT[StrictNumber]:
    ...


@overload
def sign(a: ArrayTLike[StrictNumber], *, dims: DimHints = ..., **kwargs: Any) -> ArrayT[StrictNumber]:
    ...


sign = vectorize2(sgn, doc="Return the sign of a number.", params=1)


def prod(a: ArrayTLike[StrictNumber] | StrictNumber) -> StrictNumber:
    """Return the product."""

    s = shape(a)
    l = len(s)
    if l == 0:
        return math.prod([a])  # type: ignore[list-item]
    return math.prod(flatiter(a, shape=s) if l > 1 else a) # type: ignore[arg-type]


def allclose(a: ArrayTLike[StrictNumber], b: ArrayTLike[StrictNumber], **kwargs: Any) -> bool:
    """Test if all are close."""

    return all(isclose(a, b, **kwargs) if kwargs else isclose(a, b))


@overload  # type: ignore[no-overload-impl]
def multiply(
    a: StrictNumber,
    b: StrictNumber,
    *,
    dims: DimHints = ...
) -> StrictNumber:
    ...


@overload
def multiply(
    a: VectorTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def multiply(
    a: StrictNumber,
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def multiply(
    a: MatrixTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


@overload
def multiply(
    a: StrictNumber | VectorTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


@overload
def multiply(
    a: TensorTLike[StrictNumber],
    b: StrictNumber | ArrayTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber]:
    ...


@overload
def multiply(
    a: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    b: TensorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber]:
    ...


multiply = vectorize2(operator.mul, doc="Multiply two arrays or floats.")


@overload  # type: ignore[no-overload-impl]
def divide(a: StrictNumber, b: StrictNumber, *, dims: DimHints = ...) -> float:
    ...


@overload
def divide(
    a: StrictNumber | VectorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[float]:
    ...


@overload
def divide(
    a: VectorTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[float]:
    ...


@overload
def divide(
    a: MatrixTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[float]:
    ...


@overload
def divide(
    a: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[float]:
    ...


@overload
def divide(
    a: TensorTLike[StrictNumber],
    b: StrictNumber | ArrayTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[float]:
    ...


@overload
def divide(
    a: StrictNumber | ArrayTLike[StrictNumber],
    b: TensorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[float]:
    ...


divide = vectorize2(operator.truediv, doc="Divide two arrays or floats.")


@overload  # type: ignore[no-overload-impl]
def add(
    a: StrictNumber,
    b: StrictNumber,
    *,
    dims: DimHints = ...
) -> StrictNumber:
    ...


@overload
def add(
    a: StrictNumber | VectorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def add(
    a: VectorTLike[StrictNumber],
    b: StrictNumber,
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def add(
    a: MatrixTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


@overload
def add(
    a: StrictNumber | VectorTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


@overload
def add(
    a: TensorTLike[StrictNumber],
    b: StrictNumber | ArrayTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber]:
    ...


@overload
def add(
    a: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    b: TensorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber]:
    ...


add = vectorize2(operator.add, doc="Add two arrays or floats.")


@overload  # type: ignore[no-overload-impl]
def subtract(
    a: StrictNumber,
    b: StrictNumber,
    *,
    dims: DimHints = ...
) -> StrictNumber:
    ...


@overload
def subtract(
    a: StrictNumber | VectorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def subtract(
    a: VectorTLike[StrictNumber],
    b: StrictNumber,
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def subtract(
    a: MatrixTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


@overload
def subtract(
    a: StrictNumber | VectorTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


@overload
def subtract(
    a: TensorTLike[StrictNumber],
    b: StrictNumber | ArrayTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber]:
    ...


@overload
def subtract(
    a: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    b: TensorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> TensorT[StrictNumber]:
    ...


subtract = vectorize2(operator.sub, doc="Subtract two arrays or floats.")


@overload  # type: ignore[no-overload-impl]
def multiply_x3(
    a: StrictNumber,
    b: StrictNumber,
    *,
    dims: DimHints = ...
) -> StrictNumber:
    ...


@overload
def multiply_x3(
    a: StrictNumber | VectorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def multiply_x3(
    a: VectorTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def multiply_x3(
    a: MatrixTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


@overload
def multiply_x3(
    a: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


multiply_x3 = vectorize2(
    operator.mul,
    doc="Multiply two arrays or floats.\n\nOptimized for scalars, dimensions <= 2, and vectors of lengths of 3.",
    only_x3=True
)


@overload  # type: ignore[no-overload-impl]
def divide_x3(a: StrictNumber, b: StrictNumber, *, dims: DimHints = ...) -> float:
    ...


@overload
def divide_x3(
    a: StrictNumber | VectorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[float]:
    ...


@overload
def divide_x3(
    a: VectorTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[float]:
    ...


@overload
def divide_x3(
    a: MatrixTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[float]:
    ...


@overload
def divide_x3(
    a: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[float]:
    ...


divide_x3 = vectorize2(
    operator.truediv,
    doc="Divide two arrays or floats.\n\nOptimized for scalars, dimensions <= 2, and vectors of lengths of 3.",
    only_x3=True
)


@overload  # type: ignore[no-overload-impl]
def add_x3(
    a: StrictNumber,
    b: StrictNumber,
    *,
    dims: DimHints = ...
) -> StrictNumber:
    ...


@overload
def add_x3(
    a: StrictNumber | VectorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def add_x3(
    a: VectorTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def add_x3(
    a: MatrixTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


@overload
def add_x3(
    a: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


add_x3 = vectorize2(
    operator.add,
    doc="Add two arrays or floats.\n\nOptimized for scalars, dimensions <= 2, and vectors of lengths of 3.",
    only_x3=True
)


@overload  # type: ignore[no-overload-impl]
def subtract_x3(
    a: StrictNumber,
    b: StrictNumber,
    *,
    dims: DimHints = ...
) -> StrictNumber:
    ...


@overload
def subtract_x3(
    a: StrictNumber | VectorTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def subtract_x3(
    a: VectorTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> VectorT[StrictNumber]:
    ...


@overload
def subtract_x3(
    a: MatrixTLike[StrictNumber],
    b: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


@overload
def subtract_x3(
    a: StrictNumber | VectorTLike[StrictNumber] | MatrixTLike[StrictNumber],
    b: MatrixTLike[StrictNumber],
    *,
    dims: DimHints = ...
) -> MatrixT[StrictNumber]:
    ...


subtract_x3 = vectorize2(
    operator.sub,
    doc="Subtract two arrays or floats.\n\nOptimized for scalars, dimensions <= 2, and vectors of lengths of 3.",
    only_x3=True
)


@overload
def full(array_shape: EmptyShape, fill_value: Number | ArrayTLike[Number]) -> Number:
    ...

@overload
def full(array_shape: int | VectorShape, fill_value: Number | ArrayTLike[Number]) -> VectorT[Number]:
    ...


@overload
def full(array_shape: MatrixShape, fill_value: Number | ArrayTLike[Number]) -> MatrixT[Number]:
    ...


@overload
def full(array_shape: TensorShape, fill_value: Number | ArrayTLike[Number]) -> TensorT[Number]:
    ...


def full(array_shape: int | Shape, fill_value: Number | ArrayTLike[Number]) -> ArrayT[Number] | Number:
    """Create and fill a shape with the given values."""

    # Ensure `shape` is a sequence of sizes
    s = (array_shape,) if not isinstance(array_shape, Sequence) else tuple(array_shape)

    # Handle scalar target
    if not s:
        if not isinstance(fill_value, Sequence):
            return fill_value
        _s = shape(fill_value)
        if math.prod(_s) == 1:
            return ravel(fill_value, shape=_s)[0]

    # Normalize `fill_value` to be an array.
    elif not isinstance(fill_value, Sequence):
        m = []  # type: ArrayT[Number]
        with ArrayBuilder(m, s) as build:
            for v in [fill_value] * math.prod(s):
                next(build).append(v)
        return m

    # If the shape doesn't fit the data, try and broadcast it.
    # If it does fit, just reshape it.
    if shape(fill_value) != s:
        return broadcast_to(fill_value, s)  # type: ignore[arg-type]
    return ascopy(fill_value)


@overload
def ones(array_shape: EmptyShape) -> float:
    ...


@overload
def ones(array_shape: int | VectorShape) -> VectorT[float]:
    ...


@overload
def ones(array_shape: MatrixShape) -> MatrixT[float]:
    ...


@overload
def ones(array_shape: TensorShape) -> TensorT[float]:
    ...


def ones(array_shape: int | Shape) -> ArrayT[float] | float:
    """Create and fill a shape with ones."""

    return full(array_shape, 1.0)  # type: ignore[arg-type]


@overload
def zeros(array_shape: EmptyShape) -> float:
    ...

@overload
def zeros(array_shape: int | VectorShape) -> VectorT[float]:
    ...


@overload
def zeros(array_shape: MatrixShape) -> MatrixT[float]:
    ...


@overload
def zeros(array_shape: TensorShape) -> TensorT[float]:
    ...


def zeros(array_shape: int | Shape) -> ArrayT[float] | float:
    """Create and fill a shape with zeros."""

    return full(array_shape, 0.0)  # type: ignore[arg-type]


def ndindex(*s: Shape) -> Iterator[tuple[int, ...]]:
    """Iterate dimensions."""

    yield from it.product(
        *(range(d) for d in (s[0] if not isinstance(s[0], int) and len(s) == 1 else s))  # type: ignore[arg-type]
    )


def ndenumerate(a: ArrayTLike[Number] | Number) -> Iterator[tuple[Shape, Any]]:
    """Iterate dimensions."""

    for idx in ndindex(shape(a)):
        t = a  # type: Any
        for i in idx:
            t = t[i]
        yield idx, t


class ArrayBuilder(Generic[Number]):
    """Auto drain an iterator."""

    def __init__(self, a: ArrayT[Number], s: Shape) -> None:
        """Initialize."""

        self.i = self._new_array_builder(a, s)

    def __enter__(self) -> Iterator[Any]:
        """Enter."""

        return self.i

    def __exit__(self: Any, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Drain the iterator."""

        for _ in self.i:  # pragma: no cover
            pass

    @staticmethod
    def _new_array_builder(a: ArrayT[Number], s: Shape) -> Iterator[Any]:
        """Generate a new array based on the specified size returning each row for appending."""

        dims = len(s)
        empty = not s or s[-1] == 0
        for idx in ndindex(s if not empty else (s[:-1] + (1,))):
            t = a  # type: Any
            for d in range(dims - 1):
                if not t:
                    for _ in range(s[d]):
                        t.append([])  # noqa: PERF401
                t = t[idx[d]]
            if not empty:
                yield t


class MultiArrayBuilder(ArrayBuilder[Number]):
    """Auto drain an iterator."""

    def __init__(self, a: Sequence[ArrayT[Number]], s: Sequence[Shape]) -> None:
        """Initialize."""

        self.mi = [self._new_array_builder(_a, _s) for _a, _s in it.zip_longest(a, s)]

    def __enter__(self) -> list[Iterator[Any]]:  # type: ignore[override]
        """Enter."""

        return self.mi

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Drain the iterator."""

        for i in self.mi:
            for _ in i:  # pragma: no cover
                pass


def flatiter(array: Number | ArrayTLike[Number], *, shape: Shape | None = None) -> Iterator[Number]:
    """Traverse an array returning values."""

    for indices in ndindex(_shape(array) if shape is None else shape):
        m = array  # type: Any
        for i in indices:
            m = m[i]
        yield m


def ravel(array: Number | ArrayTLike[Number], *, shape: Shape | None = None) -> VectorT[Number]:
    """Return a flattened vector."""

    return list(flatiter(array, shape=shape))


def _frange(start: float, stop: float, step: float) -> Iterator[float]:
    """Float range."""

    x = start
    rev = step < 0.0
    limit = stop - step
    while x >= limit if rev else x <= limit:
        yield x
        x += step


def arange(
    start: StrictNumber,
    stop: StrictNumber | None = None,
    step: StrictNumber = 1
) -> VectorT[float]:
    """
    Like arrange, but handles floats as well.

    Return will be a list instead of an iterator.
    Due to floating point precision, floats may be inaccurate to some degree.
    """

    if stop is None:
        stop = start
        start = 0

    if isinstance(start, int) and isinstance(stop, int) and isinstance(step, int):
        value = [*range(start, stop, step)]  # type: ignore[arg-type]
    else:
        value = [*_frange(float(start), float(stop), float(step))]  # type: ignore[arg-type]
    return value


@overload
def transpose(array: Number) -> Number:
    ...


@overload
def transpose(array: VectorTLike[Number]) -> VectorT[Number]:
    ...


@overload
def transpose(array: MatrixTLike[Number]) -> MatrixT[Number]:
    ...


@overload
def transpose(array: TensorTLike[Number]) -> TensorT[Number]:
    ...


def transpose(array: ArrayTLike[Number] | Number) -> Number | ArrayT[Number]:
    """
    A simple transpose of a matrix.

    `numpy` offers the ability to specify different axes, but right now,
    we don't have a need for that, nor the desire to figure it out :).
    """

    s = shape(array)  # type: Shape
    si = s[::-1]
    l = len(s)

    # Number
    if l == 0:
        return array  # type: ignore[return-value]
    # Vector
    if l == 1:
        return [*array]  # type: ignore[misc]
    # 2 x 2 matrix
    if l == 2:
        return [[*z] for z in zip(*array)]  # type: ignore[has-type, misc]

    # N x M matrix
    if si and si[0] == 0:
        si = si[1:] + (0,)
        total = math.prod(si[:-1])
    else:
        total = math.prod(si)

    # Create the array
    m = []  # type: ArrayT[Number]

    # Calculate data sizes
    dims = len(si)
    length = si[-1]

    # Initialize indexes so we can properly write our data
    idx = [0] * dims
    data = flatiter(array, shape=s)

    # Traverse the provided array filling our new array
    for i in range(total):

        # Navigate to the proper index to start writing data.
        # If the dimension hasn't been created yet, create it.
        t = m  # type: Any
        for d in range(dims - 1):
            if not t:
                for _ in range(si[d]):
                    t.append([])  # noqa: PERF401
            t = t[idx[d]]

        # Initialize the last dimension
        # so we can index at the correct position
        if not t:
            t[:] = [0] * length

        # Write the data
        if length:
            t[idx[-1]] = next(data)

        # Update the current indexes if we aren't done copying data.
        if i < (total - 1):
            for x in range(dims):
                if (idx[x] + 1) % si[x] == 0:
                    idx[x] = 0
                    x += 1
                else:
                    idx[x] += 1
                    break

    return m


@overload
def reshape(array: ArrayTLike[Number] | Number, new_shape: EmptyShape) -> Number:
    ...


@overload
def reshape(array: ArrayTLike[Number] | Number, new_shape: int | VectorShape) -> VectorT[Number]:
    ...


@overload
def reshape(array: ArrayTLike[Number] | Number, new_shape: MatrixShape) -> MatrixT[Number]:
    ...


@overload
def reshape(array: ArrayTLike[Number] | Number, new_shape: TensorShape) -> TensorT[Number]:
    ...


def reshape(array: ArrayTLike[Number] | Number, new_shape: int | Shape) -> Number | ArrayT[Number]:
    """Change the shape of an array."""

    # Ensure floats are arrays
    if not isinstance(array, Sequence):
        array = [array]

    # Normalize shape specifier to a sequence
    if not isinstance(new_shape, Sequence):
        new_shape = (new_shape,)

    # Shape to a scalar
    if not new_shape:
        v = ravel(array)
        if len(v) == 1:
            return v[0]
        # Kick out if the requested shape doesn't match the data
        raise ValueError(f'Shape {new_shape} does not match the data total of {shape(array)}')

    current_shape = shape(array)

    # Copy the array and quit if we are already the requested shape
    if current_shape == new_shape:
        return ascopy(array)

    empty = (not new_shape or 0 in new_shape) and (not current_shape or 0 in current_shape)

    # Make sure we can actually reshape.
    total = math.prod(new_shape if not empty else new_shape[:-1])
    if not empty and total != math.prod(current_shape):
        raise ValueError(f'Shape {new_shape} does not match the data total of {shape(array)}')

    # Create the array
    m = []  # type: ArrayT[Number]
    with ArrayBuilder(m, new_shape) as build:
        # Create an iterator to traverse the data
        for data in flatiter(array, shape=current_shape) if len(current_shape) > 1 else iter(array):
            next(build).append(data)

    return m


@overload
def shape(a: Number, *, quick: bool = ...) -> EmptyShape:
    ...


@overload
def shape(a: VectorTLike[Number], *, quick: bool = ...) -> VectorShape:
    ...


@overload
def shape(a: MatrixTLike[Number], *, quick: bool = ...) -> MatrixShape:
    ...


@overload
def shape(a: TensorTLike[Number], *, quick: bool = ...) -> TensorShape:
    ...


def shape(a: ArrayTLike[Number] | Number, *, quick: bool = False) -> Shape:
    """Get the shape of a list."""

    # Perform a quick shape calculation that will not validate all indexes.
    # This can allow a ragged shape to slip through, but is much faster.
    if quick:
        t = a  # type: Any
        s = []
        while isinstance(t, Sequence):
            l = len(t)
            s.append(l)
            if not l:
                break
            t = t[0]
        return tuple(s)

    # Found a scalar input
    if not isinstance(a, Sequence):
        return ()

    # Get the length
    size = len(a)

    # Array is empty, return the shape
    if not size:
        return (size,)

    # Recursively get the shape of the first entry and compare against the others
    first = shape(a[0])
    for r in range(1, size):
        if shape(a[r]) != first:
            raise ValueError('Ragged lists are not supported')

    # Construct the final shape
    return (size,) + first


_shape = shape


def fill_diagonal(
    matrix: MatrixT[Number] | TensorT[Number],
    val: Number | ArrayTLike[Number],
    wrap: bool = False
) -> None:
    """Fill an N-D matrix diagonal."""

    s = shape(matrix)
    if len(s) < 2:
        raise ValueError('Arrays must be 2D or greater')
    if len(s) != 2:
        wrap = False
        if min(s) != max(s):
            raise ValueError('Arrays larger than 2D must have all dimensions of equal length')

    val = [val] if not isinstance(val, Sequence) else ravel(val)
    mx = max(s)
    dlast = len(s) - 1
    dlen = len(val) - 1
    pos = 0

    x = [0] * len(s)
    while x[0] < mx:
        t = matrix  # type: Any
        for idx in range(len(s)):
            r = s[idx]
            current = x[idx]
            if current < r:
                if idx == dlast:
                    t[current] = val[pos]
                else:
                    t = t[current]
                x[idx] += 1
            elif wrap and idx and current == r:
                x[idx] = 0
            else:
                x[0] = mx
                break

        pos = pos + 1 if pos < dlen else 0


def eye(n: int, m: int | None = None, k: int = 0) -> MatrixT[float]:
    """Create a diagonal of ones in a zero initialized matrix at the specified position."""

    if m is None:
        m = n

    # Length of diagonal
    dlen = m if n > m and k < 0 else (m - abs(k))

    a = []  # type: MatrixT[float]
    for i in range(n):
        pos = i + k
        idx = i if k >= 0 else pos
        d = int(0 <= idx < dlen)  # Number of diagonals to insert (0 or 1)
        a.append(
            ([0.0] * clamp(pos, 0, m)) +
            ([1.0] * d) +
            ([0.0] * clamp(m - pos - d, 0, m))
        )
    return a


def identity(size: int) -> MatrixT[float]:
    """Create an identity matrix."""

    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


@overload
def diag(array: VectorTLike[Number], k: int = ...) -> MatrixT[Number]:
    ...


@overload
def diag(array: MatrixTLike[Number], k: int = ...) -> VectorT[Number]:
    ...


def diag(
    array: VectorTLike[Number] | MatrixTLike[Number],
    k: int = 0
) -> VectorT[Number] | MatrixT[Number]:
    """Create a diagonal matrix from a vector or return a vector of the diagonal of a matrix."""

    s = shape(array)
    dims = len(s)
    if not dims or dims > 2:
        raise ValueError('Array must be 1-D or 2-D in shape')

    if dims == 1:

        t = array[0].__class__  # type: type[Number]  # type: ignore[assignment]
        # Calculate size of matrix to accommodate the diagonal
        size = s[0] - k if k < 0 else (s[0] + k if k else s[0])
        maximum = size - 1
        minimum = 0

        # Create a diagonal matrix with the provided vector
        m = []  # type: MatrixT[Number]
        for i in range(size):
            pos = i + k
            idx = i if k >= 0 else pos
            m.append(
                ([t(0)] * clamp(pos, minimum, maximum)) +
                [array[idx] if (0 <= pos < size) else t(0)] +  # type: ignore[arg-type]
                ([t(0)] * clamp(size - pos - 1, minimum, maximum))
            )
        return m
    else:
        # Extract the requested diagonal from a rectangular 2-D matrix
        size = s[1]  # type: ignore[misc]
        d = []
        for i, r in enumerate(array):
            pos = i + k
            if (0 <= pos < size):
                d.append(r[pos])  # type: ignore[index]
        return d


@overload
def lu(
    matrix: MatrixTLike[StrictNumber],
    *,
    permute_l: Literal[True],
    p_indices: Literal[True] | Literal[False] | bool = False,
    shape: Shape | None
) -> tuple[MatrixT[float], MatrixT[float]]:
    ...


@overload
def lu(
    matrix: MatrixTLike[StrictNumber],
    *,
    permute_l: Literal[False] = False,
    p_indices: Literal[True],
    shape: Shape | None
) -> tuple[VectorT[int], MatrixT[float], MatrixT[float]]:
    ...


@overload
def lu(
    matrix: MatrixTLike[StrictNumber],
    *,
    permute_l: Literal[False] = False,
    p_indices: Literal[False] = False,
    shape: Shape | None
) -> tuple[MatrixT[float], MatrixT[float], MatrixT[float]]:
    ...


@overload
def lu(
    matrix: MatrixTLike[StrictNumber],
    *,
    permute_l: Literal[False] = False,
    p_indices: bool,
    shape: Shape | None
) -> (
    tuple[MatrixT[float], MatrixT[float], MatrixT[float]] |
    tuple[VectorT[int], MatrixT[float], MatrixT[float]]
):
    ...


@overload
def lu(
    matrix: MatrixTLike[StrictNumber],
    *,
    permute_l: bool,
    p_indices: bool,
    shape: Shape | None
) -> (
    tuple[MatrixT[float], MatrixT[float]] |
    tuple[MatrixT[float], MatrixT[float], MatrixT[float]] |
    tuple[VectorT[int], MatrixT[float], MatrixT[float]]
):
    ...


@overload
def lu(
    matrix: TensorTLike[StrictNumber],
    *,
    permute_l: Literal[True],
    p_indices: Literal[True] | Literal[False] | bool = False,
    shape: Shape | None
) -> tuple[TensorT[float], TensorT[float]]:
    ...


@overload
def lu(
    matrix: TensorTLike[StrictNumber],
    *,
    permute_l: Literal[False] = False,
    p_indices: Literal[True],
    shape: Shape | None
) -> tuple[MatrixT[int], TensorT[float], TensorT[float]]:
    ...


@overload
def lu(
    matrix: TensorTLike[StrictNumber],
    *,
    permute_l: Literal[False] = False,
    p_indices: Literal[False] = False,
    shape: Shape | None
) -> tuple[TensorT[float], TensorT[float], TensorT[float]]:
    ...


@overload
def lu(
    matrix: TensorTLike[StrictNumber],
    *,
    permute_l: Literal[False] = False,
    p_indices: bool,
    shape: Shape | None
) -> (
    tuple[TensorT[float], TensorT[float], TensorT[float]] |
    tuple[MatrixT[int], TensorT[float], TensorT[float]]
):
    ...

@overload
def lu(
    matrix: TensorTLike[StrictNumber],
    *,
    permute_l: bool,
    p_indices: bool,
    shape: Shape | None
) -> (
    tuple[TensorT[float], TensorT[float]] |
    tuple[TensorT[float], TensorT[float], TensorT[float]] |
    tuple[MatrixT[int], TensorT[float], TensorT[float]]
):
    ...


def lu(
    matrix: MatrixTLike[StrictNumber] | TensorTLike[StrictNumber],
    *,
    permute_l: bool = False,
    p_indices: bool = False,
    shape: Shape | None = None
) ->  (
    tuple[MatrixT[float], MatrixT[float]] |
    tuple[TensorT[float], TensorT[float]] |
    tuple[MatrixT[float], MatrixT[float], MatrixT[float]] |
    tuple[TensorT[float], TensorT[float], TensorT[float]] |
    tuple[VectorT[int], MatrixT[float], MatrixT[float]] |
    tuple[MatrixT[int], TensorT[float], TensorT[float]]
):
    """
    Calculate `LU` decomposition.

    P is returned as `PA = UL` or `A = P'UL` which follows `Matlab` and `Octave` opposed to `Scipy` which returns P as
    `A = PUL` or `P'A = UL`. For matrix inverse, we need P such that `PA = UL` and it is faster not having to invert
    P, even if we can invert it fairly fast as it is just a shuffled identity matrix.

    P is returned as a permutation matrix unless `p_indices` is true, in which case `P` would be returned as
    a vector containing the indexes such that `A[P,:] = L*U`.

    If `permute_l` is true, only L and U will be returned such that `P = LU`.

    Reference: https://www.statlect.com/matrix-algebra/Gaussian-elimination
               https://www.sciencedirect.com/topics/mathematics/partial-pivoting
    """

    s = _shape(matrix) if shape is None else shape
    size = s[0]
    dims = len(s)

    # We need a rectangular N x M matrix
    if dims < 2:
        raise ValueError('LU decomposition requires an array larger than a vector')
    elif dims > 2:
        last = s[-2:]  # type: tuple[int, int] # type: ignore[assignment]
        first = s[:-2]  # type: Shape
        rows = cast('MatrixTLike[StrictNumber]', list(_extract_rows(matrix, s)))
        step = last[-2]
        lt = []  # type: TensorT[float]
        ut = []  # type: TensorT[float]
        if not permute_l:
            pt = []  # type: Any
            builder = MultiArrayBuilder([pt, lt, ut], [first, first, first])
        else:
            builder = MultiArrayBuilder([lt, ut], [first, first])

        with builder as arrays:
            for r in range(0, len(rows), step):
                if not permute_l:
                    r1 = lu(rows[r:r + step], permute_l=False, p_indices=p_indices, shape=last)
                    next(arrays[0]).append(r1[0])
                    next(arrays[1]).append(r1[1])
                    next(arrays[2]).append(r1[2])
                else:
                    r2 = lu(rows[r:r + step], permute_l=True, p_indices=p_indices, shape=last)
                    next(arrays[0]).append(r2[0])
                    next(arrays[1]).append(r2[1])
        if permute_l:
            return lt, ut
        return pt, lt, ut

    # Wide or tall matrices
    wide = tall = False
    diff = s[0] - s[1]
    empty = diff == s[0]
    fmatrix = [[float(c) for c in row] for row in cast('MatrixTLike[StrictNumber]', matrix)]
    if not empty and diff:
        # Wide
        if diff < 0:
            diff = abs(diff)
            size = s[1]
            wide = True
            for _ in range(diff):
                fmatrix.append([0.0] * size)  # noqa: PERF401
        # Tall
        else:
            tall = True
            for row in fmatrix:
                row.extend([0.0] * diff)

    # Initialize the triangle matrices along with the permutation matrix.
    if empty:
        p = [] # type: Any
        l = fmatrix
        u = []
        size = 0
    else:
        if p_indices or permute_l:
            p = list(range(size))
            l = identity(size)
        else:
            p = identity(size)
            l = [list(row) for row in p]
        u = fmatrix

    # Create upper and lower triangle in 'u' and 'l'. 'p' tracks the permutation (relative position of rows)
    for i in range(size - 1):

        # Partial pivoting: identify the row with the maximal value in the column
        j = i
        maximum = abs(u[i][i])
        for k in range(i + 1, size):
            a = abs(u[k][i])
            if a > maximum:
                j = k
                maximum = a

        # Partial pivoting: Swap rows
        if j != i:
            # Exchange current upper triangle row with row with maximal value at pivot
            # Update permutation matrix as well
            u[i], u[j] = u[j], u[i]
            p[i], p[j] = p[j], p[i]

            # Only swap columns up to the pivot for the lower triangle,
            # if on first row, there is nothing to swap
            if i:
                l[i][:i], l[j][:i] = l[j][:i], l[i][:i]

        # Zero at pivot point, nothing to do
        elif not maximum:
            continue

        # We have a pivot point, let's zero out everything above and below
        # the 'l' and 'u' diagonal respectively
        for j in range(i + 1, size):
            scalar = u[j][i] / u[i][i]
            for k in range(i, size):
                u[j][k] += -u[i][k] * scalar
                l[j][k] += l[i][k] * scalar

    # Clean up the wide and tall matrices
    if tall:
        l = [r[:-diff] for r in l]
        u = [r[:-diff] for r in u][:-diff]
    elif wide:
        l = [r[:-diff] for r in l][:-diff]
        u = u[:-diff]
        p = p[:-diff] if p_indices else [r[:-diff] for r in p][:-diff]

    # Transpose the indexes and return LU after permuting L
    if permute_l:
        pt = [0] * size
        for e, i in enumerate(p):
            pt[i] = e
        p = pt

        return [l[i] for i in pt], u

    return p, l, u


def _forward_sub_vector(a: MatrixT[float], b: VectorT[float], size: int) -> VectorT[float]:
    """Forward substitution for solution of `L x = b`."""

    for i in range(size):
        v = b[i]
        for j in range(i):
            v -= a[i][j] * b[j]
        b[i] = v / a[i][i]
    return b


def _forward_sub_matrix(a: MatrixT[float], b: MatrixT[float], s: ArrayShape) -> MatrixT[float]:
    """Forward substitution for solution of `L x = b` where `b` is a matrix."""

    size1, size2 = s
    for i in range(size1):
        v = b[i]
        for j in range(i):
            for k in range(size2):
                v[k] -= a[i][j] * b[j][k]
        for j in range(size2):
            v[j] /= a[i][i]
    return b


def _back_sub_vector(a: MatrixT[float], b: VectorT[float], size: int) -> VectorT[float]:
    """Back substitution for solution of `U x = b`."""

    for i in range(size - 1, -1, -1):
        v = b[i]
        for j in range(i + 1, size):
            v -= a[i][j] * b[j]
        b[i] = v / a[i][i]
    return b


def _back_sub_matrix(a: MatrixT[float], b: MatrixT[float], s: ArrayShape) -> MatrixT[float]:
    """Back substitution for solution of `U x = b`."""

    size1, size2 = s
    for i in range(size1 - 1, -1, -1):
        v = b[i]
        for j in range(i + 1, size1):
            for k in range(size2):
                v[k] -= a[i][j] * b[j][k]
        for j in range(size2):
            b[i][j] /= a[i][i]
    return b


def _householder_reduction_bidiagonal(
    m: int,
    n: int,
    e: VectorT[float],
    u: MatrixT[float],
    q: VectorT[float],
    tol: float
) -> tuple[float, int, float, float]:
    """Householder's reduction to bidiagonal form."""

    g = x = y = 0.0
    l = 0

    for i in range(n):
        e[i] = g
        s = 0.0
        l = i + 1

        for j in range(i, m):
            s += u[j][i] ** 2

        if s < tol:
            g = 0.0

        else:
            f = u[i][i]
            g = math.sqrt(s)
            if f >= 0.0:
                g = -g
            h = f * g - s
            u[i][i] = f - g

            for j in range(l, n):
                s = 0.0

                for k in range(i,m):
                    s += u[k][i] * u[k][j]

                f = s / h

                for k in range(i, m):
                    u[k][j] += f * u[k][i]

        q[i] = g
        s = 0.0

        for j in range(l,n):
            s += u[i][j] ** 2

        if s < tol:
            g = 0.0

        else:
            f = u[i][i + 1]

            g = math.sqrt(s)
            if f >= 0.0:
                g = -g

            h = f * g - s
            u[i][i + 1] = f - g

            for j in range(l, n):
                e[j] = u[i][j] / h

            for j in range(l, m):
                s = 0.0
                for k in range(l, n):
                    s += u[j][k] * u[i][k]

                for k in range(l, n):
                    u[j][k] += s * e[k]

        y = abs(q[i]) + abs(e[i])

        if y > x:
            x = y

    return g, l, x, y


def _accumulate_right_transfrom(
    n: int,
    g: float,
    l: int,
    e: VectorT[float],
    u: MatrixT[float],
    v: MatrixT[float]
) -> float:
    """Accumulation of right hand transformations."""

    for i in range(n - 1, -1, -1):
        if g != 0.0:
            h = g * u[i][i + 1]

            for j in range(l, n):
                v[j][i] = u[i][j] / h

            for j in range(l, n):
                s = 0.0

                for k in range(l , n):
                    s += u[i][k] * v[k][j]

                for k in range(l, n):
                    v[k][j] += s * v[k][i]

        for j in range(l, n):
            v[i][j] = 0.0
            v[j][i] = 0.0

        v[i][i] = 1.0
        g = e[i]
        l = i

    return g


def _accumulate_left_transform(
    m: int,
    n: int,
    g: float,
    l: int,
    u: MatrixT[float],
    q: VectorT[float]
) -> float:
    """Accumulation of left hand transformations."""

    for i in range(n - 1, -1, -1):
        l = i + 1
        g = q[i]

        for j in range(l, n):
            u[i][j] = 0.0

        if g != 0.0:
            h = u[i][i] * g

            for j in range(l, n):
                s = 0.0

                for k in range(l, m):
                    s += u[k][i] * u[k][j]

                f = s / h
                for k in range(i, m):
                    u[k][j] +=  f * u[k][i]

            for j in range(i, m):
                u[j][i] = u[j][i] / g

        else:
            for j in range(i, m):
                u[j][i] = 0.0

        u[i][i] += 1.0

    return g


def _compute_orthogonal_rotation(a: float, b: float) -> tuple[float, float, float]:
    """Compute orthogonal rotation avoiding divide by zero."""

    d = math.sqrt(a ** 2 + b ** 2)
    if d != 0:
        return a / d, b / d, d
    return 0.0, 1.0, 0.0


def _diagonalization_of_bidiagonal(
    m: int,
    n: int,
    g: float,
    x: float,
    y: float,
    e: VectorT[float],
    u: MatrixT[float],
    q: VectorT[float],
    v: MatrixT[float],
    eps: float
) -> None:
    """Diagonalization of the bidiagonal form."""

    l = 0
    eps = eps * x
    for k in range(n - 1, -1, -1):
        maxiter = 50
        while maxiter:

            # Test f splitting
            cancel = False
            for l in range(k, -1, -1):
                if abs(e[l]) <= eps:
                    break

                if abs(q[l-1]) <= eps:
                    cancel = True
                    break

            if cancel:
                # Cancellation of e[l] if l>0
                c = 0.0
                s = 1.0
                l1 = l - 1

                for i in range(l, k + 1):
                    f = s * e[i]
                    e[i] = c * e[i]

                    if abs(f) <= eps:  # pragma: no cover
                        break

                    g = q[i]
                    c, s, h = _compute_orthogonal_rotation(g, -f)
                    q[i] = h
                    for j in range(m):
                        y = u[j][l1]
                        z = u[j][i]
                        u[j][l1] = y * c + z * s
                        u[j][i] = -y * s + z * c

            # Test f convergence
            z = q[k]
            if l == k:
                # Convergence
                if z < 0.0:
                    # q[k] is made non-negative
                    q[k] = -z
                    for j in range(n):
                        v[j][k] = -v[j][k]
                break

            # Shift from bottom 2x2 minor
            # TODO: Is it possible that h, y, or x will be zero here?
            # If so, the two f calculations could cause a divide by zero.
            # If we can find a case, we can decide how to move forward.
            x = q[l]
            y = q[k - 1]
            g = e[k - 1]
            h = e[k]
            f = ((y - z) * (y + z) + (g - h) * (g + h)) / (2.0 * h * y)
            g = math.hypot(f, 1.0)
            fg = f - g if f < 0 else f + g
            f = ((x - z) * (x + z) + h * (y / fg - h)) / x

            # Next QR transformation
            c = s = 1.0
            for i in range(l + 1, k + 1):
                g = e[i]
                y = q[i]
                h = s * g
                g = c * g
                c, s, z = _compute_orthogonal_rotation(f, h)
                e[i - 1] = z
                f = x * c + g * s
                g = -x * s + g * c
                h = y * s
                y = y * c

                for j in range(n):
                    x = v[j][i - 1]
                    z = v[j][i]
                    v[j][i - 1] = x * c + z * s
                    v[j][i] = -x * s + z * c

                c, s, z = _compute_orthogonal_rotation(f, h)
                q[i-1] = z
                f = c * g + s * y
                x = -s * g + c * y

                for j in range(m):
                    y = u[j][i - 1]
                    z = u[j][i]
                    u[j][i-1] = y * c + z * s
                    u[j][i] = -y * s + z * c

            e[l] = 0.0
            e[k] = f
            q[k] = x

            maxiter -= 1
        else:  # pragma: no cover
            raise ValueError('Could not converge on an SVD solution')


@overload
def _svd(
    a: MatrixTLike[StrictNumber],
    m: int,
    n: int,
    full_matrices: bool,
    compute_uv: Literal[False]
) ->  VectorT[float]:
    ...


@overload
def _svd(
    a: MatrixTLike[StrictNumber],
    m: int,
    n: int,
    full_matrices: bool,
    compute_uv: Literal[True] = True
) ->  tuple[MatrixT[float], VectorT[float], MatrixT[float]]:
    ...


@overload
def _svd(
    a: MatrixTLike[StrictNumber],
    m: int,
    n: int,
    full_matrices: bool,
    compute_uv: bool,
) ->  tuple[MatrixT[float], VectorT[float], MatrixT[float]] | VectorT[float]:
    ...


def _svd(
    a: MatrixTLike[StrictNumber],
    m: int,
    n: int,
    full_matrices: bool = True,
    compute_uv: bool = True
) -> tuple[MatrixT[float], VectorT[float], MatrixT[float]] | VectorT[float]:
    """
    Compute the singular value decomposition of a matrix.

    Handbook Series Linear Algebra
    Singular Value Decomposition and Least Squares Solutions
    G. H. Golub and C. Reinsch
    https://people.duke.edu/~hpgavin/SystemID/References/Golub+Reinsch-NM-1970.pdf

    Some small changes were made to support wide and tall matrices. Additionally,
    we fixed some cases where divide by zero could occur and confirmed that the
    solutions still yielded `A = U∑V^T`.
    """

    eps = EPS
    tol = MIN_FLOAT / EPS

    u = [[float(c) for c in row] for row in a]
    square = m == n
    wide = not square and m < n
    diff = 0

    if wide:
        u = transpose(u)
        m, n = n, m

    if full_matrices and not square:
        diff = m - n
        for r in u:
            r.extend([0.0] * diff)
        n = m

    e = [0.0] * n
    q = [0.0] * n
    v = zeros((n, n))

    g, l, x, y = _householder_reduction_bidiagonal(m, n, e, u, q, tol)
    if compute_uv:
        g = _accumulate_right_transfrom(n, g, l, e, u, v)
        g = _accumulate_left_transform(m, n, g, l, u, q)
    _diagonalization_of_bidiagonal(m, n, g, x, y, e, u, q, v, eps)

    if full_matrices and not square:
        if compute_uv:
            del v[-diff:]
            for r in v:
                del r[-diff:]
        del q[-diff:]

    if compute_uv:
        if wide:
            v, u = u, v

    if compute_uv:
        return u, q, v
    return q


@overload
def svd(
    a: MatrixTLike[StrictNumber],
    full_matrices: bool,
    compute_uv: Literal[False]
) -> VectorT[float]:
    ...


@overload
def svd(
    a: MatrixTLike[StrictNumber],
    full_matrices: bool,
    compute_uv: Literal[True] = True,
) -> tuple[MatrixT[float], VectorT[float], MatrixT[float]]:
    ...


@overload
def svd(
    a: MatrixTLike[StrictNumber],
    full_matrices: bool,
    compute_uv: bool,
) -> tuple[MatrixT[float], VectorT[float], MatrixT[float]] | VectorT[float]:
    ...


@overload
def svd(
    a: TensorTLike[StrictNumber],
    full_matrices: bool,
    compute_uv: Literal[False]
) ->  MatrixT[float] | TensorT[float]:
    ...


@overload
def svd(
    a: TensorTLike[StrictNumber],
    full_matrices: bool,
    compute_uv: Literal[True] = True
) ->  tuple[TensorT[float], MatrixT[float] | TensorT[float], TensorT[float]]:
    ...


@overload
def svd(
    a: TensorTLike[StrictNumber],
    full_matrices: bool,
    compute_uv: bool
) ->  tuple[TensorT[float], MatrixT[float] | TensorT[float], TensorT[float]] | MatrixT[float] | TensorT[float]:
    ...


def svd(
    a: MatrixTLike[StrictNumber] | TensorTLike[StrictNumber],
    full_matrices: bool = True,
    compute_uv: bool = True
) -> (
    tuple[MatrixT[float], VectorT[float], MatrixT[float]] |
    tuple[TensorT[float], MatrixT[float] | TensorT[float], TensorT[float]] |
    MatrixT[float] | TensorT[float] | VectorT[float]
):
    """
    Compute the singular value decomposition of a matrix.

    This differs from Numpy in that it returns `U, S, V` instead of `U, S, V^T`.

    There are far more efficient and modern algorithms than what we have implemented here.
    This approach is not recommended for very large matrices as it will be too slow. While
    it is sufficient for computing smaller matrices, it is not practical for very large
    matrices, such as compressing images with thousands of pixels. If you are doing serious
    computations with very large matrices, Numpy or SciPy should be strongly considered.
    """

    s = shape(a)
    dims = len(s)

    # Ensure we have at least a matrix
    if dims < 2:
        raise ValueError('Array must be at least 2 dimensional')

    # Handle stacked matrix cases
    elif dims > 2:
        last = s[-2:]  # type: tuple[int, int] # type: ignore[misc]
        first = s[:-2]  # type: Shape # type: ignore[misc]
        rows = cast('MatrixTLike[StrictNumber]', list(_extract_rows(a, s)))
        step = last[-2]
        m, n = last
        sigma = []  # type: ArrayT[float]
        if compute_uv:
            u = []  # type: MatrixT[float] | TensorT[float]
            v = []  # type: MatrixT[float] | TensorT[float]
            builder = MultiArrayBuilder([u, sigma, v], [first, first, first])
        else:
            builder = MultiArrayBuilder([sigma], [first])
        with builder as arrays:
            for r in range(0, len(rows), step):
                if compute_uv:
                    uv_result = _svd(rows[r:r + step], m, n, full_matrices, True)
                    next(arrays[0]).append(uv_result[0])
                    next(arrays[1]).append(uv_result[1])
                    next(arrays[2]).append(uv_result[2])
                else:
                    s_result = _svd(rows[r:r + step], m, n, full_matrices, False)
                    next(arrays[0]).append(s_result)
        if compute_uv:
            return u, sigma, v  # type: ignore[return-value]
        return sigma

    if compute_uv:
        return _svd(cast('MatrixTLike[StrictNumber]', a), s[0], s[1], full_matrices, True)
    return _svd(cast('MatrixTLike[StrictNumber]', a), s[0], s[1], full_matrices, False)


@overload
def svdvals(a: TensorTLike[StrictNumber]) -> MatrixT[float] | TensorT[float]:
    ...


@overload
def svdvals(a: MatrixTLike[StrictNumber]) -> VectorT[float]:
    ...


def svdvals(a: MatrixTLike[StrictNumber] | TensorTLike[StrictNumber]) -> ArrayT[float]:
    """Get the s values from SVD."""

    return svd(a, False, False)


@overload
def _qr(
    a: MatrixT[float],
    m: int,
    n: int,
    mode: Literal['reduced'] = "reduced"
) -> tuple[MatrixT[float], MatrixT[float]]:
    ...

@overload
def _qr(
    a: MatrixT[float],
    m: int,
    n: int,
    mode: Literal['complete']
) -> tuple[MatrixT[float], MatrixT[float]]:
    ...


@overload
def _qr(
    a: MatrixT[float],
    m: int,
    n: int,
    mode: Literal['r']
) -> MatrixT[float]:
    ...


@overload
def _qr(
    a: MatrixT[float],
    m: int,
    n: int,
    mode: Literal['raw']
) -> tuple[MatrixT[float], VectorT[float]]:
    ...


@overload
def _qr(
    a: MatrixT[float],
    m: int,
    n: int,
    mode: str
) -> tuple[MatrixT[float], MatrixT[float]] | tuple[MatrixT[float], VectorT[float]] | MatrixT[float]:
    ...


def _qr(a: MatrixT[float], m: int, n: int, mode: str = 'reduced') -> (
    tuple[MatrixT[float], MatrixT[float]] |
    tuple[MatrixT[float], VectorT[float]] |
    MatrixT[float]
):
    """Perform QR decomposition on a matrix."""

    # Setup configuration flags
    mode_raw = mode_r = mode_complete = False
    if mode == 'r':
        mode_r = True
        mode_raw = mode_complete = False
    elif mode == 'complete':
        mode_complete = True
        mode_r = mode_raw = False
    elif mode == 'raw':
        mode_raw = mode_r = True
        mode_complete = False

    # Initialize Q and R and make adjustments for wide or tall matrices
    r = a
    square = m == n
    empty = not n
    wide = not square and m < n
    tall = not wide and not square
    diff = 0
    if wide:
        diff = n - m
        for _ in range(diff):
            r.append([0.0] * n)
    elif tall:
        diff = m - n

    q = identity(m)

    # Initialize containers for householder reflections and tau values if raw mode
    if mode_raw:
        h = []
        tau = [0.0] * (m if not tall else n)

    for k in range(0, m - 1 if not tall else n):
        # Calculate the householder reflections
        norm = math.sqrt(sum([r[i][k] ** 2 for i in range(k, m)]))
        sig = -sgn(r[k][k])
        u0 = r[k][k] - sig * norm
        w = [[(r[i][k] / u0) if u0 else 1] for i in range(k, m)]
        w[0][0] = 1
        t = (-sig * u0 / norm) if norm else 0
        wtw = matmul(w, [[x[0] * t for x in w]], dims=D2)

        # Capture householder reflections and tau
        if mode_raw:
            h.append(w)
            tau[k] = t

        # Update R
        sub_r = [r[i][:] for i in range(k, m)]
        for count, row in enumerate(matmul(wtw, sub_r, dims=D2), k):
            # Fill the lower triangle with zeros and update the upper triangle
            r[count][:] = [r[count][col] - row[col] for col in range(n)]

        if not mode_r:
            # Update Q
            sub_q = [row[k:] for row in q]
            for count, row in enumerate(matmul(sub_q, wtw, dims=D2)):
                q[count][k:] = [sub_q[count][i] - row[i] for i in range(m - k)]

    # Zero out the lower triangle or fill with the householder reflectors if in raw mode
    for k in range(0, m - 1 if not tall else n):
        for j, i in enumerate(range(k + 1, m), 1):
            r[i][k] = h[k][j][0] if mode_raw else 0.0

    # Trim unnecessary columns and rows
    if tall and not mode_complete and not empty:
        for row in q:
            del row[-diff:]
        del r[-diff:]
    elif wide:
        del r[-diff:]

    # Return H (householder reflections in the lower half of R matrix) and tau values
    if mode_raw:
        return r, tau

    # Return either Q and R or just R depending on the mode
    return r if mode_r else (q, r)


@overload
def qr(
    a: MatrixTLike[StrictNumber],
    mode: Literal['reduced'] = "reduced"
) -> tuple[MatrixT[float], MatrixT[float]]:
    ...

@overload
def qr(
    a: MatrixTLike[StrictNumber],
    mode: Literal['complete']
) -> tuple[MatrixT[float], MatrixT[float]]:
    ...


@overload
def qr(
    a: MatrixTLike[StrictNumber],
    mode: Literal['r']
) -> MatrixT[float]:
    ...


@overload
def qr(
    a: MatrixTLike[StrictNumber],
    mode: Literal['raw']
) -> tuple[MatrixT[float], VectorT[float]]:
    ...


@overload
def qr(
    a: MatrixTLike[StrictNumber],
    mode: str
) -> tuple[MatrixT[float], MatrixT[float]] | tuple[MatrixT[float], VectorT[float]] | MatrixT[float]:
    ...


@overload
def qr(
    a: TensorTLike[StrictNumber],
    mode: Literal['reduced'] = "reduced"
) -> tuple[TensorT[float], TensorT[float]]:
    ...

@overload
def qr(
    a: TensorTLike[StrictNumber],
    mode: Literal['complete']
) -> tuple[TensorT[float], TensorT[float]]:
    ...


@overload
def qr(
    a: TensorTLike[StrictNumber],
    mode: Literal['r']
) -> TensorT[float]:
    ...


@overload
def qr(
    a: TensorTLike[StrictNumber],
    mode: Literal['raw']
) -> tuple[TensorT[float], MatrixT[float] | TensorT[float]]:
    ...


@overload
def qr(
    a: TensorTLike[StrictNumber],
    mode: str
) -> (
    tuple[TensorT[float], TensorT[float]] |
    tuple[TensorT[float], MatrixT[float] |
    TensorT[float]] | TensorT[float]
):
    ...


def qr(
    a: MatrixTLike[StrictNumber] | TensorTLike[StrictNumber],
    mode: str = 'reduced'
) -> (
    tuple[MatrixT[float], MatrixT[float]] |
    tuple[MatrixT[float], VectorT[float]] |
    MatrixT[float] |
    tuple[TensorT[float], TensorT[float]] |
    tuple[TensorT[float], MatrixT[float] | TensorT[float]] |
    TensorT[float]
):
    """
    QR decomposition using householder reflections.

    https://www.cs.cornell.edu/~bindel/class/cs6210-f09/lec18.pdf

    Generally this provides a similar interface to Numpy with the following modes:

    - "reduced": returns Q, R with dimensions `(…, M, K)`, `(…, K, N)`
    - "complete": returns Q, R with dimensions `(…, M, M)`, `(…, M, N)`
    - "r": returns R only with dimensions `(…, K, N)`
    - "raw": returns h, tau with dimensions `(…, N, M)`, `(…, K,)` where
      h is the R matrix with the householder reflections in the lower triangle.
      Unlike Numpy, we do not provide the transposed matrix for Fortran.
    """

    if mode not in QR_MODES:
        raise ValueError(f"Mode '{mode}' not recognized")

    s = shape(a)
    dims = len(s)
    mode_r = mode == 'r' or mode == 'raw'

    # Ensure we have at least a matrix
    if dims < 2:
        raise ValueError('Array must be at least 2 dimensional')

    # Handle stacked matrix cases
    elif dims > 2:
        last = s[-2:]  # type: tuple[int, int] # type: ignore[misc]
        first = s[:-2]  # type: Shape # type: ignore[misc]
        rows = list(_extract_rows(a, s))
        step = last[-2]
        m, n = last
        r = []  # type: MatrixT[float]
        if not mode_r:
            q = []  # type: MatrixT[float]
            builder = MultiArrayBuilder([q, r], [first, first])
        else:
            builder = MultiArrayBuilder([r], [first])
        with builder as arrays:
            for ri in range(0, len(rows), step):
                result = _qr([[float(co) for co in ro]for ro in rows[ri:ri + step]], m, n, mode)
                if not mode_r:
                    next(arrays[0]).append(result[0])
                    next(arrays[1]).append(result[1])
                else:
                    next(arrays[0]).append(result)
        if mode_r:
            return r
        return q, r

    # Apply QR decomposition on a single matrix
    return _qr([[float(c) for c in row] for row in a], s[0], s[1], mode)  # type: ignore[arg-type]


def matrix_rank(a: MatrixTLike[StrictNumber] | TensorTLike[StrictNumber]) -> Any:
    """Calculate the matrix rank."""

    s = shape(a)
    dims = len(s)
    last = s[-2:]  # type: tuple[int, int] # type: ignore[misc]
    rtol = max(last) * EPS

    if dims < 2:
        raise ValueError('Array must be at least 2 dimensional')

    # Single matrix
    if dims == 2:
        rank = 0
        sigma = _svd(cast('MatrixTLike[StrictNumber]', a), s[0], s[1], full_matrices=False, compute_uv=False)
        tol = max(sigma) * rtol
        for x in sigma:
            if x > tol:
                rank += 1
        return rank

    # Stack of matrices
    first = s[:-2]  # type: Shape # type: ignore[misc]
    rows = list(_extract_rows(a, s))
    step = last[-2]
    m, n = last
    ranks = []  # type: ArrayT[float]
    with ArrayBuilder(ranks, first) as build:
        for r in range(0, len(rows), step):
            sigma = _svd(rows[r:r + step], m, n, full_matrices=False, compute_uv=False)
            rank = 0
            tol = max(sigma) * rtol
            for x in sigma:
                if x > tol:
                    rank += 1
            next(build).append(rank)
    return ranks


@overload
def solve(a: MatrixTLike[StrictNumber], b: VectorTLike[StrictNumber]) -> VectorT[float]:
    ...


@overload
def solve(a: MatrixTLike[StrictNumber], b: MatrixTLike[StrictNumber]) -> MatrixT[float]:
    ...


@overload
def solve(a: MatrixTLike[StrictNumber], b: TensorTLike[StrictNumber]) -> TensorT[float]:
    ...


@overload
def solve(a: TensorTLike[StrictNumber], b: VectorTLike[StrictNumber]) -> MatrixT[float] | TensorT[float]:
    ...


@overload
def solve(a: TensorTLike[StrictNumber], b: MatrixTLike[StrictNumber] | TensorTLike[StrictNumber]) -> TensorT[float]:
    ...


def solve(a: MatrixTLike[StrictNumber] | TensorTLike[StrictNumber], b: ArrayTLike[StrictNumber]) -> ArrayT[float]:
    """
    Solve the system of equations for `x` where `ax = b`.

    Normal broadcasting applies and the behavior matches Numpy 2+.
    """

    s = shape(a)
    size = s[-1]
    dims = len(s)
    if len(s) < 2 or s[-1] != s[-2]:
        raise ValueError('Last two dimension must be square')

    # Fast simple cases: two 2 dimensional matrices or one 2 dimensional matrix and a vector
    dim1 = not isinstance(b[0], Sequence)
    dim2 = not dim1 and not isinstance(b[0][0], Sequence)  # type: ignore[index]
    if dims == 2 and (dim1 or dim2):
        # Get the LU decomposition
        p, l, u = lu(cast('MatrixTLike[StrictNumber]', a), p_indices=True, shape=s)

        # If determinant is zero, we can't solve. Really small determinant may give bad results.
        if math.prod(l[i][i] * u[i][i] for i in range(size)) == 0.0:
            raise ValueError('Matrix is singular')

        # Solve for x using forward substitution on U and back substitution on L
        if dim2:
            b = cast('MatrixTLike[StrictNumber]', b)
            # Two matrices
            size2 = len(b[0])
            if size != len(b):
                raise ValueError('Mismatched dimensions')

            ordered = []  # type: MatrixT[float]
            for i in p:
                r = b[i]
                if len(r) != size2:
                    raise ValueError('Mismatched dimensions')
                ordered.append(list(r))
            s2 = (size, size2)  # type: Shape
            return _back_sub_matrix(u, _forward_sub_matrix(l, ordered, s2), s2)

        # Matrix and one vector
        b = cast('VectorTLike[StrictNumber]', b)
        if len(b) != s[-2]:
            raise ValueError('Mismatched dimensions')
        b = [b[i] for i in p]
        return _back_sub_vector(u, _forward_sub_vector(l, b, size), size)  # type: ignore[arg-type]

    # More complex, deeply nested cases that require more analyzing
    s2 = shape(b)
    m = []  # type: ArrayT[float]

    # Matrices and vectors
    if dim1:
        m_shape = s[-2:]  # type: ignore[misc]
        base_shape = s[:-2] # type: ignore[misc]

        with ArrayBuilder(m, base_shape) as build:
            for idx in ndindex(base_shape):
                ma = a  # type: Any
                for i in idx:
                    ma = ma[i]

                p, l, u = lu(ma, p_indices=True, shape=m_shape)

                if math.prod(l[i][i] * u[i][i] for i in range(size)) == 0.0:  # pragma: no cover
                    raise ValueError('Matrix is singular')

                next(build).append(_back_sub_vector(u, _forward_sub_vector(l, [b[i] for i in p], size), size))  # type: ignore[misc]
        return m

    # Matrices and matrices
    new_shape = _broadcast_shape((s[:-1], s2[:-1]), max(dims - 1, len(s2) - 1))  # type: ignore[misc]
    base_shape = new_shape[:-1]
    a = broadcast_to(a, new_shape + s[-1:])  # type: ignore[assignment, arg-type, misc]
    b = broadcast_to(b, new_shape + s2[-1:])  # type: ignore[assignment, arg-type, misc]
    with ArrayBuilder(m, base_shape) as build:
        for idx in ndindex(base_shape):
            ma = a
            for i in idx:
                ma = ma[i]
            mb = b  # type: Any
            for i in idx:
                mb = mb[i]

            p, l, u = lu(ma, p_indices=True, shape=s[-2:])  # type: ignore[misc]

            if math.prod(l[i][i] * u[i][i] for i in range(size)) == 0.0:
                raise ValueError('Matrix is singular')

            bi = [list(mb[i]) for i in p]
            s3 = (size, len(bi[0]))
            next(build).append(_back_sub_matrix(u, _forward_sub_matrix(l, bi, s3), s3))
    return m


def trace(matrix: MatrixTLike[StrictNumber]) -> StrictNumber:
    """Sum the diagonal."""

    return sum(diag(matrix))


@overload
def det(array: MatrixTLike[StrictNumber]) -> float:
    ...


@overload
def det(array: TensorTLike[StrictNumber]) -> VectorT[float]:
    ...


def det(array: MatrixTLike[StrictNumber] | TensorTLike[StrictNumber]) -> float | VectorT[float]:
    """Get the determinant."""

    s = shape(array)
    if len(s) < 2 or s[-1] != s[-2]:
        raise ValueError('Last two dimensions must be square')
    if len(s) == 2:
        size = s[0]
        p, l, u = lu(cast('MatrixTLike[StrictNumber]', array), shape=s)
        swaps = size - trace(p)
        _sign = (-1) ** (swaps - 1) if swaps else 1
        dt = cast('float', _sign * math.prod(l[i][i] * u[i][i] for i in range(size)))
        return 0.0 if not dt else dt
    else:
        last = s[-2:]  # type: ignore[misc]
        rows = list(_extract_rows(array, s))
        step = last[-2]
        return [det(rows[r:r + step]) for r in range(0, len(rows), step)]


@overload
def inv(matrix: MatrixTLike[StrictNumber]) -> MatrixT[float]:
    ...


@overload
def inv(matrix: TensorTLike[StrictNumber]) -> TensorT[float]:
    ...


def inv(matrix: MatrixTLike[StrictNumber] | TensorTLike[StrictNumber]) -> MatrixT[float] | TensorT[float]:
    """Invert the matrix using `LU` decomposition."""

    # Ensure we have a square matrix
    s = shape(matrix)
    dims = len(s)
    last = s[-2:]  # type: tuple[int, int] # type: ignore[misc]
    if dims < 2 or min(last) != max(last):
        raise ValueError('Matrix must be a N x N matrix')

    # Handle dimensions greater than 2 x 2
    elif dims > 2:
        invert = []  # type: TensorT[float]
        step = last[-2]
        rows = list(_extract_rows(matrix, s))
        with ArrayBuilder(invert, s[:-2]) as build:  # type: ignore[misc]
            for r in range(0, len(rows), step):
                next(build).append(inv(rows[r:r + step]))
        return invert

    # Calculate the LU decomposition.
    size = s[0]
    p, l, u = lu(cast('MatrixTLike[StrictNumber]', matrix), shape=s)

    # Floating point math will produce very small, non-zero determinants for singular matrices.
    # This occurs with Numpy as well.
    # Don't bother calculating sign as we only care about how close to zero we are.
    if math.prod(l[i][i] * u[i][i] for i in range(size)) == 0.0:
        raise ValueError('Matrix is singular')

    # Solve for the identity matrix (will give us inverse)
    # Permutation matrix is the identity matrix, even if shuffled.
    s2 = (size, size)
    return _back_sub_matrix(u, _forward_sub_matrix(l, p, s2), s2)


@overload
def pinv(a: MatrixTLike[StrictNumber]) -> MatrixT[float]:
    ...


@overload
def pinv(a: TensorTLike[StrictNumber]) -> TensorT[float]:
    ...


def pinv(a: MatrixTLike[StrictNumber] | TensorTLike[StrictNumber]) -> MatrixT[float] | TensorT[float]:
    """
    Compute the (Moore-Penrose) pseudo-inverse of a matrix using SVD.

    Negative results can be returned, use `fnnls` for a non-negative solution (if possible).
    """

    s = shape(a)
    dims = len(s)

    # Ensure we have at least a matrix
    if dims < 2:
        raise ValueError('Array must be at least 2 dimensional')

    elif dims > 2:
        last = s[-2:]  # type: tuple[int, int] # type: ignore[misc]
        invert = []  # type: TensorT[float]
        rows = list(_extract_rows(a, s))
        step = last[-2]
        with ArrayBuilder(invert, s[:-2]) as build:  # type: ignore[misc]
            for r in range(0, len(rows), step):
                next(build).append(pinv(rows[r:r + step]))
        return invert

    m = s[0]
    n = s[1]
    u, sigma, v = _svd(cast('MatrixTLike[StrictNumber]', a), m, n, full_matrices=False)
    tol = max(sigma) * max(m, n) * EPS
    sigma = [[1 / x if x > tol else x] for x in sigma]  # type: ignore[]
    return matmul(v, multiply(sigma, transpose(u), dims=D2), dims=D2)


@overload
def vstack(
    arrays: Sequence[Number | VectorTLike[Number] | MatrixTLike[Number]]
) -> MatrixT[Number]:
    ...


@overload
def vstack(
    arrays: Sequence[TensorTLike[Number]]
) -> TensorT[Number]:
    ...


def vstack(
    arrays: Sequence[ArrayTLike[Number] | Number]
) -> MatrixT[Number] | TensorT[Number]:
    """Vertical stack."""

    m = []  # type: list[Any]
    dims = 0

    # Array tracking for verification
    axis = 0
    last = ()  # type: Shape
    last_dims = 0

    for a in arrays:
        s = shape(a)
        dims = len(s)

        # We need to be working with at least a 2D array
        if dims == 0:
            a = [[a]]  # type: ignore[assignment]
            s = (1, 1)
            dims = 2
        elif dims == 1:
            a = [a]  # type: ignore[assignment]
            s = (1, s[0])  # type: ignore[misc]
            dims = 2

        # Verify that we can apply the stacking
        if last:
            end2 = min(last_dims, dims)
            end1 = min(end2, axis)
            start = 1
            start2 = min(end1 + 1, end2)
            # All axes must match except for the concatenation axis
            if s[start:end1] + s[start2:end2] != last[start:end1] + last[start2:end2]:
                raise ValueError('All the input array dimensions except for the concatenation axis must match exactly')

        # Stack the arrays
        m.extend(reshape(a, (math.prod(s[:1 - dims]),) + s[1 - dims:-1] + s[-1:]))  # type: ignore[arg-type, misc]

        # Update the last array tracker
        if not last or len(last) > len(s):
            last = s
            last_dims = dims

    # Fail if we have nothing to stack
    if not m:
        raise ValueError("'vstack' requires at least one array")

    return m


def _hstack_extract(a: ArrayTLike[Number] | Number, shape: ArrayShape) -> Iterator[ArrayT[Number]]:
    """Extract data from the second axis."""

    data = flatiter(a, shape=shape)
    length = math.prod(shape[1:])

    for _ in range(shape[0]):
        yield [next(data) for _ in range(length)]


def hstack(arrays: Sequence[ArrayTLike[Number] | Number]) -> ArrayT[Number]:
    """Horizontal stack."""

    # Gather up shapes
    columns = 0
    shapes = []
    orig_shapes = []

    # Array tracking for verification
    axis = 1
    last = ()  # type: Shape
    last_dims = 0
    largest = ()  # type: Shape
    largest_length = 0

    arrs = []
    for a in arrays:
        s = shape(a)
        orig_shapes.append(s)
        dims = len(s)

        # Ensure we are at least 1-D
        if dims == 0:
            a = [a]  # type: ignore[assignment]
            s = (1,)
            dims = 1

        # Store modified arrays to use later
        arrs.append(a)

        # Get the largest
        l = len(s)
        if l > largest_length:
            largest = s
            largest_length = l

        # Verify that we can apply the stacking
        if last:
            end2 = min(last_dims, dims)
            end1 = min(end2, axis)
            start = 0
            start2 = min(end1 + 1, end2)
            max_dims = max(last_dims, dims)
            # All axes must match except for the concatenation axis. 1-D arrays can have different lengths.
            if (max_dims > 1 and s[start:end1] + s[start2:end2] != last[start:end1] + last[start2:end2]):
                raise ValueError('All the input array dimensions except for the concatenation axis must match exactly')

        # Gather up shapes and tally the size of axis 1, 1-D arrays do not need this.
        if dims > 1:
            columns += s[axis]

        shapes.append(s)

        # Update the last array tracker
        if not last or len(last) > len(s):
            last = s
            last_dims = dims

    # Fail if we have nothing to stack
    if not shapes:
        raise ValueError("'hstack' requires at least one array")

    # Handle 1-D vector cases
    if largest_length == 1:
        m1 = []  # type: VectorT[Number]
        for a, s in zip(arrays, orig_shapes):
            m1.extend(ravel(a, shape=s))
        return m1

    # Iterate the arrays returning the content per second axis
    m = []  # type: Any
    for data in it.zip_longest(*[_hstack_extract(a, s) for a, s in it.zip_longest(arrs, shapes) if s != (0,)]):
        for d in data:
            m.extend(d)

    # Shape the data to the new shape
    new_shape = largest[:axis] + (columns,) + largest[axis + 1:] if len(largest) > 1 else (columns,)
    return reshape(m, new_shape)  # type: ignore[no-any-return, arg-type]


def outer(
    a: StrictNumber | ArrayTLike[StrictNumber],
    b: StrictNumber | ArrayTLike[StrictNumber]
) -> MatrixT[StrictNumber]:
    """Compute the outer product of two vectors (or flattened matrices)."""

    v2 = ravel(b)
    return [[x * y for y in v2] for x in flatiter(a)]


@overload
def inner(a: StrictNumber, b: StrictNumber) -> StrictNumber:
    ...


@overload
def inner(a: StrictNumber, b: VectorTLike[StrictNumber]) -> VectorT[StrictNumber]:
    ...


@overload
def inner(a: VectorTLike[StrictNumber], b: StrictNumber) -> VectorT[StrictNumber]:
    ...


@overload
def inner(a: StrictNumber, b: MatrixTLike[StrictNumber]) -> MatrixT[StrictNumber]:
    ...


@overload
def inner(a: MatrixTLike[StrictNumber], b: StrictNumber) -> MatrixT[StrictNumber]:
    ...


@overload
def inner(a: StrictNumber, b: TensorTLike[StrictNumber]) -> TensorT[StrictNumber]:
    ...


@overload
def inner(a: TensorTLike[StrictNumber], b: StrictNumber) -> TensorT[StrictNumber]:
    ...


@overload
def inner(a: VectorTLike[StrictNumber], b: VectorTLike[StrictNumber]) -> StrictNumber:
    ...


@overload
def inner(a: VectorTLike[StrictNumber], b: MatrixTLike[StrictNumber]) -> VectorT[StrictNumber]:
    ...


@overload
def inner(a: MatrixTLike[StrictNumber], b: VectorTLike[StrictNumber]) -> VectorT[StrictNumber]:
    ...


@overload
def inner(a: VectorTLike[StrictNumber], b: TensorTLike[StrictNumber]) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def inner(a: TensorTLike[StrictNumber], b: VectorTLike[StrictNumber]) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def inner(a: MatrixTLike[StrictNumber], b: MatrixTLike[StrictNumber]) -> MatrixT[StrictNumber]:
    ...


@overload
def inner(a: MatrixTLike[StrictNumber], b: TensorTLike[StrictNumber]) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def inner(a: TensorTLike[StrictNumber], b: MatrixTLike[StrictNumber]) -> TensorT[StrictNumber] | MatrixT[StrictNumber]:
    ...


@overload
def inner(a: TensorTLike[StrictNumber], b: TensorTLike[StrictNumber]) -> TensorT[StrictNumber]:
    ...


def inner(
    a: StrictNumber | ArrayTLike[StrictNumber],
    b: StrictNumber | ArrayTLike[StrictNumber]
) -> StrictNumber | ArrayT[StrictNumber]:
    """Compute the inner product of two arrays."""

    shape_a = shape(a)
    shape_b = shape(b)
    dims_a = len(shape_a)
    dims_b = len(shape_b)

    # If both inputs are not scalars, the last dimension must match
    if (shape_a and shape_b and shape_a[-1] != shape_b[-1]):
        raise ValueError(f'The last dimensions {shape_a} and {shape_b} do not match')

    # If we have a scalar, we should just multiply
    if (not dims_a or not dims_b):
        return multiply(a, b, dims=(dims_a, dims_b))

    # Adjust the input so that they can properly be evaluated
    # Scalars will be broadcasted to properly match the last dimension
    # of the other input.
    if dims_a == 1:
        first = [a]  # type: Any
    elif dims_a > 2:
        first = _extract_rows(a, shape_a)  # type: ignore[arg-type]
    else:
        first = a

    if dims_b == 1:
        second = [b]  # type: Any
    elif dims_b > 2:
        second = list(_extract_rows(b, shape_b))  # type: ignore[arg-type]
    else:
        second = b

    # Perform the actual inner product
    m = [[sum([x * y for x, y in it.zip_longest(r1, r2)]) for r2 in second] for r1 in first]  # type: ArrayT[StrictNumber]
    new_shape = shape_a[:-1] + shape_b[:-1]  # type: ignore[misc]

    # Shape the data.
    return reshape(m, new_shape)  # type: ignore[arg-type]


def fnnls(
    A: MatrixTLike[StrictNumber],
    b: VectorTLike[StrictNumber],
    epsilon: float = ATOL,
    max_iters: int = 0
) -> tuple[VectorT[float], float]:
    """
    Fast non-negative least squares.

    A fast non-negativity-constrained least squares
    https://www.researchgate.net/publication/230554373_A_Fast_Non-negativity-constrained_Least_Squares_Algorithm
    Rasmus Bro and Sijmen De Jong
    Journal of Chemometrics. 11, 393-401 (1997)
    """

    m, n = shape(A, quick=True)

    if m != len(b):
        raise ValueError(f'Vector length of b must match first dimension of A: {m} != {len(b)}')

    if not max_iters:
        max_iters = n * 30

    AT = transpose(A)
    ATA = dot(AT, A, dims=D2)
    ATb = dot(AT, b, dims=D2_D1)

    x = [0.0] * n
    s = [0.0] * n
    w = subtract(ATb, dot(ATA, x, dims=D2_D1), dims=D1)  # type: VectorT[float]

    # P tracks positive elements in x
    # Does double duty as P and R vector outlined in the paper
    P = [False] * n

    # Continue until all values of x are positive (non-negative results only)
    # or we exhaust the iterations.
    count = 0
    while sum(P) < n and max(w[i] for i in range(n) if not P[i]) > epsilon and count < max_iters:
        # Find the index that maximizes w
        # This will be an index not in P
        imx = 0
        mx = -math.inf
        for i in range(n):
            if not P[i] and w[i] > mx:
                imx = i
                mx = w[i]

        P[imx] = True

        # Solve least squares problem for columns and rows not in P
        idx = [i for i in range(n) if P[i]]
        v = dot(inv([[ATA[i][j] for j in idx] for i in idx]), [ATb[i] for i in idx], dims=D2_D1)
        for i, _v in zip(idx, v):
            s[i] = _v

        # Deal with negative values
        while _any([s[i] <= epsilon for i in range(n) if P[i]]):
            count += 1

            # Calculate step size, alpha, to prevent any x from going negative
            alpha = min(
                [zdiv(x[i], (x[i] - s[i]), math.inf) for i in range(n) if P[i] * (s[i] <= epsilon)]
            )

            # Update the solution
            x = add(x, dot(alpha, subtract(s, x, dims=D1), dims=SC_D1), dims=D1)

            # Remove indexes in P where x == 0
            for i in range(n):
                if x[i] <= epsilon:
                    P[i] = False

            # Solve least squares problem again
            idx = [i for i in range(n) if P[i]]
            v = dot(inv([[ATA[i][j] for j in idx] for i in idx]), [ATb[i] for i in idx], dims=D2_D1)
            j = 0
            l = len(idx)
            for i in range(n):
                if j < l and i == idx[j]:
                    s[i] = v[j]
                    j += 1
                else:
                    s[i] = 0.0

        # Update the solution
        x = s[:]
        w = subtract(ATb, dot(ATA, x, dims=D2_D1), dims=D1)

    # Return our final result, for better or for worse
    res = math.hypot(*subtract(b, dot(A, x, dims=D2_D1), dims=D1))
    return x, res


@overload
def flip(a: Number, axis: int | tuple[int, ...] | None = ...) -> Number:
    ...


@overload
def flip(a: VectorTLike[Number], axis: int | tuple[int, ...] | None = ...) -> VectorT[Number]:
    ...


@overload
def flip(a: MatrixTLike[Number], axis: int | tuple[int, ...] | None = ...) -> MatrixT[Number]:
    ...


@overload
def flip(a: TensorTLike[Number], axis: int | tuple[int, ...] | None = ...) -> TensorT[Number]:
    ...


def flip(
    a: ArrayTLike[Number] | float,
    axis: int | tuple[int, ...] | None = None
) -> ArrayT[Number] | Number:
    """Flip specified axis/axes."""

    s = shape(a)
    l = len(s)

    if not s:
        return a  # type: ignore[return-value]

    # Adjust axes
    if axis is None:
        axes = set(range(l))
    elif isinstance(axis, int):
        axes = {l + axis if axis < 0 else axis}
    else:
        axes = set()
        for ai in axis:
            ai = l + ai if ai < 0 else ai
            if ai in axes:
                raise ValueError('Repeated axis')
            axes.add(ai)

    m = ascopy(a)  # type: ArrayT[Number]  # type: ignore[arg-type]
    indexes = [-1] * l
    end = l - 1

    # Check if axes are within bounds
    for ax in axes:
        if ax > end:
            raise ValueError(f'Axis {ax} out of bounds of dimension {l}')

    # Flip the axes
    for idx in ndindex(s[:-1] + (1,)):  # type: ignore[misc]
        t = m  # type: Any
        count = 0
        for i in idx:
            if indexes[count] == -1:
                if count in axes:
                    t[:] = t[::-1]

            if indexes[count] != i:
                indexes[count] = i
                indexes[count + 1:] = [-1] * (end - count)
            count += 1
            t = t[i]
    return m


@overload
def flipud(a: Number) -> Number:
    ...


@overload
def flipud(a: VectorTLike[Number]) -> VectorT[Number]:
    ...


@overload
def flipud(a: MatrixTLike[Number]) -> MatrixT[Number]:
    ...


@overload
def flipud(a: TensorTLike[Number]) -> TensorT[Number]:
    ...


def flipud(a: ArrayTLike[Number] | Number) -> ArrayT[Number] | Number:
    """Flip axis 0."""

    return flip(a, axis=0)


@overload
def fliplr(a: Number) -> Number:
    ...


@overload
def fliplr(a: VectorTLike[Number]) -> VectorT[Number]:
    ...


@overload
def fliplr(a: MatrixTLike[Number]) -> MatrixT[Number]:
    ...


@overload
def fliplr(a: TensorTLike[Number]) -> TensorT[Number]:
    ...


def fliplr(a: ArrayTLike[Number] | Number) -> ArrayT[Number] | Number:
    """Flip axis 1."""

    return flip(a, axis=1)


@overload
def roll(
    a: Number,
    shift: int | tuple[int, ...],
    axis: int | tuple[int, ...] | None = ...
) -> Number:
    ...


@overload
def roll(
    a: VectorTLike[Number],
    shift: int | tuple[int, ...],
    axis: int | tuple[int, ...] | None = ...
) -> VectorT[Number]:
    ...


@overload
def roll(
    a: MatrixTLike[Number],
    shift: int | tuple[int, ...],
    axis: int | tuple[int, ...] | None = ...
) -> MatrixT[Number]:
    ...


@overload
def roll(
    a: TensorTLike[Number],
    shift: int | tuple[int, ...],
    axis: int | tuple[int, ...] | None = ...
) -> TensorT[Number]:
    ...


def roll(
    a: ArrayTLike[Number] | Number,
    shift: int | tuple[int, ...],
    axis: int | tuple[int, ...] | None = None
) -> ArrayT[Number] | Number:
    """Roll specified axis/axes."""

    s = shape(a)

    # Return floats
    if not s:
        return a  # type: ignore[return-value]

    # Flatten data when no axis is specified and roll data
    if axis is None:
        if not isinstance(shift, int):
            shift = sum(shift)
        p = math.prod(s)
        _sign = sgn(shift)
        shift = shift % (p * _sign) if p and _sign else 0
        flat = ravel(a, shape=s) if len(s) != 1 else [*a]  # type: ignore[misc]
        sh = -shift
        flat[:] = flat[sh:] + flat[:sh]
        return reshape(flat, s)

    axes = [axis] if isinstance(axis, int) else axis
    m = ascopy(cast('ArrayT[Number]', a))
    l = len(s)
    indexes = [-1] * l
    end = l - 1

    # Broadcast the shifts and axes
    new_shift = []  # type: VectorT[int]
    new_axes = []  # type: VectorT[int]
    for i, j in broadcast(shift, axes):
        i, j = i, j
        if j < 0:
            j = l + j
        _sign = sgn(i)
        new_shift.append((i % (s[j] * _sign)) if s[j] and _sign else 0)
        new_axes.append(j)

    # Perform the roll across the specified axes
    for idx in ndindex(s[:-1] + (1,)):  # type: ignore[misc]
        t = m  # type: Any
        count = 0
        for i in idx:
            if indexes[count] == -1:
                for e, ax in enumerate(new_axes):
                    if count == ax:
                        sh = -new_shift[e]
                        t[:] = t[sh:] + t[:sh]

            if indexes[count] != i:
                indexes[count] = i
                indexes[count + 1:] = [-1] * (end - count)
            count += 1
            t = t[i]
    return m
