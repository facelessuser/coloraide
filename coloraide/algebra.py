"""
Math related methods.

Includes various math related functions to aid in color translation and manipulation.

Matrix methods are implemented to mimic `numpy`. We've cherry picked what we think is the
most useful for what we do with colors. We basically implement each function according to
the API description and then verify our tested inputs and outputs match `numpy`.

We actually really like `numpy`, and have only done this to keep dependencies lightweight
and available on non C Python based implementations. If we ever decide to swap out `numpy`,
we should be able to relatively easily.

Some liberties are taken here and there. For instance, we are not as fast as `numpy`, so
we add some shortcuts to things that are used a lot (`dot`, `multiply`, `divide`, etc.).
In these cases, we provide new input to instruct the operation as to the dimensions of the
matrix so we don't waste time analyzing the matrix.

There is no requirement that color space plugins (or really any plugin) need to use
anything here, `numpy` could be used as long as the final results are converted to normal
types.
"""
from __future__ import annotations
import sys
import math
import operator
import functools
from itertools import zip_longest as zipl
from .types import ArrayLike, MatrixLike, VectorLike, Array, Matrix, Vector, SupportsFloatOrInt
from typing import Callable, Sequence, Iterator, Any, Iterable, overload  # noqa: F401

NaN = float('nan')
INF = float('inf')
EPSILON = sys.float_info.epsilon
PY38 = (3, 8) <= sys.version_info
TAU = math.pi * 2

if sys.version_info >= (3, 8):
    prod = math.prod
else:
    def prod(values: Iterable[SupportsFloatOrInt]) -> SupportsFloatOrInt:
        """Get the product of a list of numbers."""

        if not values:
            return 1

        return functools.reduce(operator.mul, values)

# Shortcut for math operations
# Specify one of these in divide, multiply, dot, etc.
# to bypass analyzing the shape to determine which path
# to take.
#
# `SC` = scalar, `D1` = 1-D array or vector, `D2` = 2-D
# matrix, and `DN_DM` means an N-D and M-D matrix.
#
# If just a single specifier is used, it is assumed that
# the operation is performed against another of the same.
# `SC` = scalar and a scalar, while `SC_D1` means a scalar
# and a vector
SC = (0, 0)
D1 = (1, 1)
D2 = (2, 2)
SC_D1 = (0, 1)
SC_D2 = (0, 2)
D1_SC = (1, 0)
D1_D2 = (1, 2)
D2_SC = (2, 0)
D2_D1 = (2, 1)
DN_DM = (3, 3)

# Vector used to create a special matrix used in natural splines
M141 = [1, 4, 1]


################################
# General math
################################
def is_nan(obj: float) -> bool:
    """Check if "not a number"."""

    return math.isnan(obj)


def no_nans(value: VectorLike | Iterable[float], default: float = 0.0) -> Vector:
    """Ensure there are no `NaN` values in a sequence."""

    return [(default if is_nan(x) else x) for x in value]


def no_nan(value: float, default: float = 0.0) -> float:
    """Convert list of numbers or single number to valid numbers."""

    return default if is_nan(value) else value


def round_half_up(n: float, scale: int = 0) -> float:
    """Round half up."""

    mult = 10.0 ** scale
    return math.floor(n * mult + 0.5) / mult


def round_to(f: float, p: int = 0) -> float:
    """Round to the specified precision using "half up" rounding."""

    # Do no rounding, just return a float with full precision
    if p == -1:
        return float(f)

    # Integer rounding
    elif p == 0:
        return round_half_up(f)

    # Ignore infinity
    elif math.isinf(f):
        return f

    # Round to the specified precision
    else:
        whole = int(f)
        digits = 0 if whole == 0 else int(math.log10(-whole if whole < 0 else whole)) + 1
        return round_half_up(whole if digits > p else f, p - digits)


def clamp(
    value: SupportsFloatOrInt,
    mn: SupportsFloatOrInt | None = None,
    mx: SupportsFloatOrInt | None = None
) -> SupportsFloatOrInt:
    """Clamp the value to the the given minimum and maximum."""

    if mn is not None and mx is not None:
        return max(min(value, mx), mn)
    elif mn is not None:
        return max(value, mn)
    elif mx is not None:
        return min(value, mx)
    else:
        return value


def cbrt(n: float) -> float:
    """Calculate cube root."""

    return nth_root(n, 3)


def nth_root(n: float, p: float) -> float:
    """Calculate nth root while handling negative numbers."""

    if p == 0:  # pragma: no cover
        return float('inf')

    if n == 0:
        # Can't do anything with zero
        return 0

    return math.copysign(abs(n) ** (p ** -1), n)


def npow(base: float, exp: float) -> float:
    """Perform `pow` with a negative number."""

    return math.copysign(abs(base) ** exp, base)


def rect_to_polar(a: float, b: float) -> tuple[float, float]:
    """Take rectangular coordinates and make them polar."""

    c = math.sqrt(a ** 2 + b ** 2)
    h = math.degrees(math.atan2(b, a)) % 360
    return c, h


def polar_to_rect(c: float, h: float) -> tuple[float, float]:
    """Take rectangular coordinates and make them polar."""

    a = c * math.cos(math.radians(h))
    b = c * math.sin(math.radians(h))
    return a, b


################################
# Interpolation and splines
################################
def lerp(p0: float, p1: float, t: float) -> float:
    """Linear interpolation."""

    return p0 + (p1 - p0) * t


@functools.lru_cache(maxsize=10)
def _matrix_141(n: int) -> Matrix:
    """Get matrix '1 4 1'."""

    m = [[0] * n for _ in range(n)]  # type: Matrix
    m[0][0:2] = M141[1:]
    m[-1][-2:] = M141[:-1]
    for x in range(n - 2):
        m[x + 1][x:x + 3] = M141
    return inv(m)


def naturalize_bspline_controls(coordinates: list[Vector]) -> None:
    """
    Given a set of B-spline control points in the Nth dimension, create new naturalized interpolation control points.

    Using the color points as `S0...Sn`, calculate `B0...Bn`, such that interpolation will
    pass through `S0...Sn`.

    When given 2 data points, the operation will be returned as linear, so there is nothing to do.
    """

    n = len(coordinates) - 2

    # Special case 3 data points
    if n == 1:
        coordinates[1] = [
            (a * 6 - (b + c)) / 4 for a, b, c in zip(coordinates[1], coordinates[0], coordinates[2])
        ]

    # Handle all other cases where n does not result in linear interpolation
    elif n > 1:
        # Create [1, 4, 1] matrix for size `n` set of control points
        m = _matrix_141(n)

        # Create C matrix from the data points
        c = []
        for r in range(1, n + 1):
            if r == 1:
                c.append([a * 6 - b for a, b in zip(coordinates[r], coordinates[r - 1])])
            elif r == n:
                c.append([a * 6 - b for a, b in zip(coordinates[n], coordinates[n + 1])])
            else:
                c.append([a * 6 for a in coordinates[r]])

        # Dot M^-1 and C to get B (control points)
        v = dot(m, c, dims=D2)
        for r in range(1, n + 1):
            coordinates[r] = v[r - 1]


def bspline(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
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


def catrom(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
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


def monotone(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
    """
    Monotone spline based on Hermite.

    We calculate our secants for our four samples (the center pair being our interpolation target).

    From those, we calculate an initial gradient, and test to see if it is needed. In the event
    that our there is no increase or decrease between the point, we can infer that the gradient
    should be horizontal. We also test if they have opposing signs, if so, we also consider the
    gradient to be zero.

    Lastly, we ensure that the gradient is confined within a circle with radius 3 as it has been
    observed that such a circle encapsulates the entire monotonicity region.

    Once gradients are calculated, we simply perform the Hermite spline calculation and clean up
    floating point math errors to ensure monotonicity.

    We could build up secant and gradient info ahead of time, but currently we do it on the fly.

    http://jbrd.github.io/2020/12/27/monotone-cubic-interpolation.html
    https://ui.adsabs.harvard.edu/abs/1990A%26A...239..443S/abstract
    https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.39.6720
    https://en.wikipedia.org/w/index.php?title=Monotone_cubic_interpolation&oldid=950478742
    """

    # Save some time calculating this once
    t2 = t ** 2
    t3 = t2 * t

    # Calculate the secants for the differing segments
    s0 = p1 - p0
    s1 = p2 - p1
    s2 = p3 - p2

    # Calculate initial gradients
    m1 = (s0 + s1) * 0.5
    m2 = (s1 + s2) * 0.5

    # Center segment should be horizontal as there is no increase/decrease between the two points
    if math.isclose(p1, p2):
        m1 = m2 = 0.0
    else:

        # Gradient is zero if segment is horizontal or if the left hand secant differs in sign from current.
        if math.isclose(p0, p1) or (math.copysign(1.0, s0) != math.copysign(1.0, s1)):
            m1 = 0.0

        # Ensure gradient magnitude is either 3 times the left or current secant (smaller being preferred).
        else:
            m1 *= min(3.0 * s0 / m1, min(3.0 * s1 / m1, 1.0))

        # Gradient is zero if segment is horizontal or if the right hand secant differs in sign from current.
        if math.isclose(p2, p3) or (math.copysign(1.0, s1) != math.copysign(1.0, s2)):
            m2 = 0.0

        # Ensure gradient magnitude is either 3 times the current or right secant (smaller being preferred).
        else:
            m2 *= min(3.0 * s1 / m2, min(3.0 * s2 / m2, 1.0))

    # Now we can evaluate the Hermite spline
    result = (
        (m1 + m2 - 2 * s1) * t3 +
        (3.0 * s1 - 2.0 * m1 - m2) * t2 +
        m1 * t +
        p1
    )

    # As the spline is monotonic, all interpolated values should be confined between the endpoints.
    # Floating point arithmetic can cause this to be out of bounds on occasions.
    mn = min(p1, p2)
    mx = max(p1, p2)
    return min(max(result, mn), mx)


SPLINES = {
    'natural': bspline,
    'bspline': bspline,
    'catrom': catrom,
    'monotone': monotone,
    'linear': lerp
}  # type: dict[str, Callable[..., float]]


class Interpolate:
    """Interpolation object."""

    def __init__(
        self,
        points: list[Vector],
        callback: Callable[..., float],
        length: int,
        linear: bool = False
    ) -> None:
        """Initialize."""

        self.length = length
        self.num_coords = len(points[0])
        self.points = list(zip(*points))
        self.callback = callback
        self.linear = linear

    def steps(self, count: int) -> list[Vector]:
        """Generate steps."""

        divisor = count - 1
        return [self(r / divisor) for r in range(0, count)]

    def __call__(self, t: float) -> Vector:
        """Interpolate."""

        n = self.length - 1
        i = max(min(math.floor(t * n), n - 1), 0)
        t = (t - i / n) * n if 0 <= t <= 1 else t
        if not self.linear:
            i += 1

        # Iterate the coordinates and apply the spline to each component
        # returning the completed, interpolated coordinate set.
        coord = []
        for idx in range(self.num_coords):
            c = self.points[idx]
            if self.linear or t < 0 or t > 1:
                coord.append(lerp(c[i], c[i + 1], t))
            else:
                coord.append(
                    self.callback(
                        c[i - 1],
                        c[i],
                        c[i + 1],
                        c[i + 2],
                        t
                    )
                )

        return coord


def interpolate(points: list[Vector], method: str = 'linear') -> Interpolate:
    """Generic interpolation method."""

    points = points[:]
    length = len(points)

    # Natural requires some preprocessing of the B-spline points.
    if method == 'natural':
        naturalize_bspline_controls(points)

    # Get the spline method
    s = SPLINES[method]
    linear = method == 'linear'

    # Clamp end points
    if not linear:
        start = [2 * a - b for a, b in zip(points[0], points[1])]
        end = [2 * a - b for a, b in zip(points[-1], points[-2])]
        points.insert(0, start)
        points.append(end)

    return Interpolate(points, s, length, linear)


################################
# Matrix/linear algebra math
################################
def vdot(a: VectorLike, b: VectorLike) -> float:
    """Dot two vectors."""

    s = 0.0
    for x, y in zipl(a, b):
        s += x * y
    return s


def vcross(v1: VectorLike, v2: VectorLike) -> Vector:  # pragma: no cover
    """
    Cross two vectors.

    Takes vectors of either 2 or 3 dimensions. If 2 dimensions, will return the z component.
    To mix 2 and 3 vector components, please use `cross` instead which will pad 2 dimension
    vectors if the other is of 3 dimensions. `cross` has more overhead, so use `cross` if
    you don't need broadcasting of any kind.
    """

    if len(v1) == len(v2) == 2:
        return [v1[0] * v2[1] - v1[1] * v2[0]]
    else:
        return [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v2[2] * v1[0],
            v1[0] * v2[1] - v1[1] * v2[0]
        ]


@overload
def acopy(a: VectorLike) -> Vector:
    ...


@overload
def acopy(a: MatrixLike) -> Matrix:
    ...


def acopy(a: ArrayLike) -> Array:
    """Array copy."""

    return [(acopy(i) if isinstance(i, Sequence) else i) for i in a]  # type: ignore[return-value]


@overload
def _cross_pad(a: VectorLike, s: tuple[int, ...]) -> Vector:
    ...


@overload
def _cross_pad(a: MatrixLike, s: tuple[int, ...]) -> Matrix:
    ...


def _cross_pad(a: ArrayLike, s: tuple[int, ...]) -> Array:
    """Pad an array with 2-D vectors."""

    m = acopy(a)

    # Initialize indexes so we can properly write our data
    total = prod(s[:-1])
    idx = [0] * (len(s) - 1)

    for c in range(total):
        t = m  # type: Any
        for i in idx:
            t = t[i]

        t.append(0)

        if c < (total - 1):
            for x in range(len(s) - 1):
                if (idx[x] + 1) % s[x] == 0:
                    idx[x] = 0
                    x += 1
                else:
                    idx[x] += 1
                    break
    return m


@overload
def cross(a: VectorLike, b: VectorLike) -> Vector:
    ...


@overload
def cross(a: MatrixLike, b: Any) -> Matrix:
    ...


@overload
def cross(a: Any, b: MatrixLike) -> Matrix:
    ...


def cross(a: ArrayLike, b: ArrayLike) -> Array:
    """Vector cross product."""

    # Determine shape of arrays
    shape_a = shape(a)
    shape_b = shape(b)
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

    if dims_a == 1:
        if dims_b == 1:
            # Cross two vectors
            return vcross(a, b)  # type: ignore[arg-type]
        elif dims_b == 2:
            # Cross a vector and a 2-D matrix
            return [vcross(a, r) for r in b]  # type: ignore[arg-type]
        else:
            # Cross a vector and an N-D matrix
            return reshape(  # type: ignore[return-value]
                [vcross(a, r) for r in _extract_dims(b, dims_b, dims_b - 1)],  # type: ignore[arg-type]
                shape_b
            )
    elif dims_a == 2:
        if dims_b == 1:
            # Cross a 2-D matrix and a vector
            return [vcross(r, b) for r in a]  # type: ignore[arg-type]
    elif dims_b == 1:
        # Cross an N-D matrix and a vector
        return reshape(  # type: ignore[return-value]
            [vcross(r, b) for r in _extract_dims(a, dims_a, dims_a - 1)],  # type: ignore[arg-type]
            shape_a
        )

    # Cross an N-D and M-D matrix
    bcast = broadcast(a, b)
    a2 = []
    b2 = []
    data = []
    count = 1
    size = bcast.shape[-1]
    for x, y in bcast:
        a2.append(x)
        b2.append(y)
        if count == size:
            data.append(vcross(a2, b2))
            a2 = []
            b2 = []
            count = 0
        count += 1
    return reshape(data, bcast.shape)  # type: ignore[return-value]


def _extract_dims(
    m: ArrayLike,
    total: int,
    target: int,
    depth: int = 0
) -> Iterator[ArrayLike]:
    """
    Extract the requested dimension.

    Mainly used only to extract the last two dimensions of a matrix.
    As not really generalized for "any" dimension, not really good to expose publicly.
    """

    if depth == target:
        if total != 1:
            yield [[x[r] for x in m] for r in range(len(m[0]))]  # type: ignore[index, arg-type]
        else:
            yield m
    else:
        for m2 in m:
            yield from _extract_dims(m2, total - 1, target, depth + 1)  # type: ignore[arg-type]


@overload
def dot(a: float, b: float, *, dims: tuple[int, int] | None = None) -> float:
    ...


@overload
def dot(a: float, b: VectorLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def dot(a: VectorLike, b: float, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def dot(a: float, b: MatrixLike, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


@overload
def dot(a: MatrixLike, b: float, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


@overload
def dot(a: VectorLike, b: VectorLike, *, dims: tuple[int, int] | None = None) -> float:
    ...


@overload
def dot(a: VectorLike, b: MatrixLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def dot(a: MatrixLike, b: VectorLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def dot(a: MatrixLike, b: MatrixLike, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


def dot(
    a: float | ArrayLike,
    b: float | ArrayLike,
    *,
    dims: tuple[int, int] | None = None
) -> float | Array:
    """
    Get dot product of simple numbers, vectors, and matrices.

    Matrices will be detected and the appropriate logic applied
    unless `dims` is provided. `dims` should simply describe the
    number of dimensions of `a` and `b`: (2, 1) for a 2D and 1D array.
    Providing `dims` will sidestep analyzing the matrix for a more
    performant operation. Anything dimensions above 2 will be treated
    as an ND x MD scenario and the actual dimensions will be extracted
    regardless due to necessity.
    """

    if dims is None or dims[0] > 2 or dims[1] > 2:
        shape_a = shape(a)
        shape_b = shape(b)
        dims_a = len(shape_a)
        dims_b = len(shape_b)

        # Handle matrices of N-D and M-D size
        if dims_a and dims_b and dims_a > 2 or dims_b > 2:
            if dims_a == 1:
                # Dot product of vector and a M-D matrix
                cols1 = list(_extract_dims(b, dims_b, dims_b - 2))  # type: ignore[arg-type]
                shape_c = shape_b[:-2] + shape_b[-1:]
                return reshape([[vdot(a, c) for c in col] for col in cols1], shape_c)  # type: ignore[arg-type]
            else:
                # Dot product of N-D and M-D matrices
                # Resultant size: `dot(xy, yz) = xz` or `dot(nxy, myz) = nxmz`
                cols2 = (
                    list(_extract_dims(b, dims_b, dims_b - 2))  # type: ignore[arg-type]
                    if dims_b > 1
                    else [[b]]  # type: ignore[list-item]
                )
                rows = list(_extract_dims(a, dims_a, dims_a - 1))  # type: ignore[arg-type]
                m2 = [
                    [[sum(multiply(row, c)) for c in col] for col in cols2]  # type: ignore[arg-type]
                    for row in rows
                ]
                shape_c = shape_a[:-1]
                if dims_b != 1:
                    shape_c += shape_b[:-2] + shape_b[-1:]
                return reshape(m2, shape_c)  # type: ignore[arg-type]

    else:
        dims_a, dims_b = dims

    # Optimize to handle arrays <= 2-D
    if dims_a == 1:
        if dims_b == 1:
            # Dot product of two vectors
            return vdot(a, b)  # type: ignore[arg-type]
        elif dims_b == 2:
            # Dot product of vector and a matrix
            return [vdot(a, col) for col in zipl(*b)]  # type: ignore[arg-type, misc]

    elif dims_a == 2:
        if dims_b == 1:
            # Dot product of matrix and a vector
            return [vdot(row, b) for row in a]  # type: ignore[arg-type, union-attr]
        elif dims_b == 2:
            # Dot product of two matrices
            return [[vdot(row, col) for col in zipl(*b)] for row in a]  # type: ignore[arg-type, misc, union-attr]

    # Trying to dot a number with a vector or a matrix, so just multiply
    return multiply(a, b, dims=(dims_a, dims_b))


def _matrix_chain_order(dims: list[tuple[int, int]]) -> list[list[int]]:
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

    n = len(dims)
    m = full((n, n), 0)  # type: Any
    s = full((n, n), 0)  # type: list[list[int]] # type: ignore[assignment]
    p = [a[0] for a in dims] + [dims[-1][1]]

    for d in range(1, n):
        for i in range(n - d):
            j = i + d
            m[i][j] = INF
            for k in range(i, j):
                cost = m[i][k] + m[k + 1][j] + p[i] * p[k + 1] * p[j + 1]
                if cost < m[i][j]:
                    m[i][j] = cost
                    s[i][j] = k
    return s


def _multi_dot(a: list[ArrayLike], s: list[list[int]], i: int, j: int) -> ArrayLike:
    """Recursively dot the matrices in the array."""

    if i != j:
        return dot(  # type: ignore[return-value]
            _multi_dot(a, s, i, int(s[i][j])),
            _multi_dot(a, s, int(s[i][j]) + 1, j),
            dims=D2
        )
    return a[i]


def multi_dot(arrays: Sequence[ArrayLike]) -> float | Array:
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
    if not isinstance(arrays, list):
        arrays = list(arrays)

    # Row vector
    if len(shapes[0]) == 1:
        arrays[0] = [arrays[0]]
        shapes[0] = (1,) + shapes[0]
        is_vector = True

    # Column vector
    if len(shapes[-1]) == 1:
        arrays[-1] = transpose([arrays[-1]])
        shapes[-1] = shapes[-1] + (1,)
        if is_vector:
            is_scalar = True
        else:
            is_vector = True

    # Make sure everything is a 2-D matrix as the next calculations only work for 2-D.
    if not all([len(s) == 2 for s in shapes]):
        raise ValueError('All arrays must be 2-D matrices')

    # No need to do the expensive and complicated chain order algorithm for only 3.
    # We can easily calculate three with less complexity and in less time. Anything
    # greater than three becomes a headache.
    if count == 3:
        pa = prod(shapes[0])
        pc = prod(shapes[2])
        cost1 = pa * shapes[2][0] + pc * shapes[0][0]
        cost2 = pc * shapes[0][1] + pa * shapes[2][1]
        if cost1 < cost2:
            value = dot(dot(arrays[0], arrays[1], dims=D2), arrays[2], dims=D2)
        else:
            value = dot(arrays[0], dot(arrays[1], arrays[2], dims=D2), dims=D2)

    # Calculate the fastest ordering with dynamic programming using memoization
    s = _matrix_chain_order([shape(a) for a in arrays])  # type: ignore[misc]
    value = _multi_dot(arrays, s, 0, count - 1)

    # `numpy` returns the shape differently depending on if there is a row and/or column vector
    if is_scalar:
        return value[0][0]  # type: ignore[no-any-return]
    elif is_vector:
        return ravel(value)
    else:
        return value  # type: ignore[no-any-return]


class _BroadcastTo:
    """
    Broadcast to a shape.

    By flattening the data, we are able to slice out the bits we need in the order we need
    and duplicate them to expand the matrix to fit the provided shape.

    We need 3 things to do this:
    - The original array.
    - The stage 1 array shape (with prepended 1s). This helps us calculate our loop iterations.
    - The new shape.
    """

    def __init__(self, array: ArrayLike | float, old: tuple[int, ...], new: tuple[int, ...]) -> None:
        """Initialize."""

        self._loop1 = 0
        self._loop2 = 0
        self._chunk_subindex = 0
        self._chunk_max = 0
        self._chunk_index = 0
        self._chunk = []  # type: list[float]

        # Unravel the data as it will be quicker to slice the data in a flattened form
        # than iterating over the dimensions to replicate the data.
        self.data = ravel(array)
        self.shape = new

        # Is the new shape actually different than the original?
        self.different = old != new

        if self.different:
            # Calculate the shape of the data.
            if len(old) > 1:
                self.amount = prod(old[:-1])
                self.length = old[-1]
            else:
                # Vectors have to be handled a bit special as they only have 1-D
                self.amount = old[-1]
                self.length = 1

            # Calculate how many times we should replicate data both horizontally and vertically
            # We need to flip them based on whether the original shape has an even or odd number of
            # dimensions.
            diff = [int(x / y) if y else y for x, y in zip(new, old)]
            repeat = prod(diff[:-1]) if len(old) > 1 else 1
            expand = diff[-1]
            if len(diff) > 1 and diff[-2] > 1:
                self.repeat = expand
                self.expand = repeat
            else:
                self.repeat = repeat
                self.expand = expand
        elif not self.data:
            # There is no data
            self.amount = self.length = self.expand = self.repeat = 0
        else:
            # There is no modifications that need to be made on this array,
            # So we'll be chunking it without any cleverness.
            self.amount = len(self.data)
            self.length = 1
            self.expand = 1
            self.repeat = 1

        self.reset()

    def reset(self) -> None:
        """Reset."""

        # Setup and return the iterator.
        self._loop1 = self.repeat
        self._loop2 = self.expand
        self._chunk_subindex = 0
        self._chunk_max = self.amount * self.length
        self._chunk_index = 0

    def __next__(self) -> float:
        """Next."""

        if self._loop1:
            # Get the data.
            d = self.data[self._chunk_index + self._chunk_subindex]

            self._chunk_subindex += 1
            if self._chunk_subindex >= self.length:
                # We've processed the entirety of the current chunk
                # Let's see if we need to process it again.
                self._loop2 -= 1
                self._chunk_subindex = 0
                if not self._loop2:
                    # We've finished processing this chunk, let's get the next.
                    self._chunk_index += self.length
                    self._loop2 = self.expand

                    if self._chunk_index >= self._chunk_max:
                        # We are actually at the end of all the data,
                        # let's see if we need to process all the data again.
                        self._loop1 -= 1
                        if self._loop1:
                            # We need to keep going
                            self._chunk_index = 0

            # Return the current data
            return d

        # We have nothing more to give
        raise StopIteration

    def __iter__(self) -> Iterator[float]:
        """Return the broadcasted array, piece by piece."""

        return self


class _SimpleBroadcast:
    """
    Special broadcast of less than 2 arrays or 2 small dimension arrays that is faster than the generalized approach.

    A single array can have any dimensions, but two arrays must have dimensions less than 2.
    """

    def __init__(self, arrays: Sequence[ArrayLike | float], shapes: Sequence[tuple[int, ...]]) -> None:
        """Initialize."""

        total = len(arrays)
        if total == 0:
            a, b = None, None  # type: tuple[Any, Any]
        elif total == 1:
            a, b = arrays[0], None
        else:
            a, b = arrays

        self.a = a
        self.dims_a = len(shapes[0]) if a is not None else 0

        self.b = b
        self.dims_b = len(shapes[1]) if b is not None else 0

        self.reset()

    def vector_broadcast(self, a: VectorLike, b: VectorLike) -> Iterator[tuple[float, ...]]:
        """Broadcast two vectors."""

        # Broadcast the vector
        if len(a) == 1:
            a = [a[0]] * len(b)
        elif len(b) == 1:
            b = [b[0]] * len(a)

        yield from zipl(a, b)

    def broadcast(
        self,
        a: ArrayLike | float | None,
        b: ArrayLike | float | None,
        dims_a: int, dims_b: int
    ) -> Iterator[tuple[float, ...]]:
        """Simple broadcast of a single array or two arrays with dimensions less than 2."""

        # Broadcast a single array case or empty set of arrays.
        if b is None:
            if a is not None:
                yield from ((i,) for i in flatiter(a))
            return

        # Inputs have matching dimensions.
        if dims_a == dims_b:
            if dims_a == 1:
                # Broadcast two vectors
                yield from self.vector_broadcast(a, b)  # type: ignore[arg-type]
            elif dims_a == 2:
                # Broadcast two 2-D matrices
                for ra, rb in zipl(a, b):  # type: ignore[arg-type]
                    yield from self.vector_broadcast(ra, rb)  # type: ignore[arg-type]
            else:
                yield a, b  # type: ignore[misc]

        # Inputs containing a scalar on either side
        elif not dims_a or not dims_b:
            if dims_a == 1:
                # Apply math to a vector and number
                for i in a:  # type: ignore[union-attr]
                    yield i, b  # type: ignore[misc]
            elif dims_b == 1:
                # Apply math to a number and a vector
                for i in b:  # type: ignore[union-attr]
                    yield a, i  # type: ignore[misc]
            elif dims_a == 2:
                # Apply math to 2-D matrix and number
                for row in a:  # type: ignore[union-attr]
                    for i in row:  # type: ignore[union-attr]
                        yield i, b  # type: ignore[misc]
            else:
                for row in b:  # type: ignore[union-attr]
                    for i in row:  # type: ignore[union-attr]
                        yield a, i  # type: ignore[misc]

        # Inputs are at least 2-D dimensions or below on both sides
        elif dims_a == 1:
            # Broadcast a vector and 2-D matrix
            for row in b:  # type: ignore[union-attr]
                yield from self.vector_broadcast(a, row)  # type: ignore[arg-type]
        else:
            # Broadcast a 2-D matrix and a vector
            for row in a:  # type: ignore[union-attr]
                yield from self.vector_broadcast(row, b)  # type: ignore[arg-type]

    def reset(self) -> None:
        """Reset."""

        self._iter = self.broadcast(self.a, self.b, self.dims_a, self.dims_b)

    def __next__(self) -> tuple[float, ...]:
        """Next."""

        # Get the next chunk of data
        return next(self._iter)

    def __iter__(self) -> Iterator[tuple[float, ...]]:
        """Iterate."""

        # Setup and and return the iterator.
        return self


class Broadcast:
    """Broadcast."""

    def __init__(self, *arrays: ArrayLike | float) -> None:
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

        # Adjust array shapes by padding out with '1's until matches max dimensions
        stage1_shapes = []
        for s in shapes:
            dims = len(s)
            if dims < max_dims:
                stage1_shapes.append(((1,) * (max_dims - dims)) + s)
            else:
                stage1_shapes.append(s)

        # Determine a common shape, if possible
        s2 = []
        for dim in zip(*stage1_shapes):
            maximum = max(dim)
            if not all([d == 1 or d == maximum for d in dim]):
                raise ValueError("Could not broadcast arrays as shapes are incompatible")
            s2.append(maximum)
        common = tuple(s2)

        # Create iterators to "broadcast to"
        total = len(arrays)
        self.simple = total < 2 or (total == 2 and len(common) <= 2)
        if self.simple:
            self.iters = [_SimpleBroadcast(arrays, shapes)]  # type: list[_BroadcastTo] | list[_SimpleBroadcast]
        else:
            self.iters = [_BroadcastTo(a, s1, common) for a, s1 in zip(arrays, stage1_shapes)]

        # I don't think this is done the same way as `numpy`.
        # But shouldn't matter for what we do.
        self.shape = common
        self.ndims = max_dims
        self.size = prod(common)
        self._init()

    def _init(self) -> None:
        """Setup main iterator."""

        self._iter = self.iters[0] if self.simple else zipl(*self.iters)

    def reset(self) -> None:
        """Reset iterator."""

        # Reset all the child iterators.
        for i in self.iters:
            i.reset()
        self._init()

    def __next__(self) -> tuple[float, ...]:
        """Next."""

        # Get the next chunk of data
        return next(self._iter)  # type: ignore[arg-type]

    def __iter__(self) -> Broadcast:
        """Iterate."""

        # Setup and and return the iterator.
        return self


def broadcast(*arrays: ArrayLike) -> Broadcast:
    """Broadcast."""

    return Broadcast(*arrays)


def broadcast_to(a: ArrayLike, s: int | Sequence[int]) -> Array:
    """Broadcast array to a shape."""

    if not isinstance(s, Sequence):
        s = (s,)

    if not isinstance(a, Sequence):
        a = [a]

    s_orig = shape(a)
    ndim_orig = len(s_orig)
    ndim_target = len(s)
    if ndim_orig > ndim_target:
        raise ValueError("Cannot broadcast {} to {}".format(s_orig, s))

    s1 = list(s_orig)
    if ndim_orig < ndim_target:
        s1 = ([1] * (ndim_target - ndim_orig)) + s1

    for d1, d2 in zip(s1, s):
        if d1 != d2 and (d1 != 1 or d1 > d2):
            raise ValueError("Cannot broadcast {} to {}".format(s_orig, s))

    m = list(_BroadcastTo(a, tuple(s1), tuple(s)))
    return reshape(m, s) if len(s) > 1 else m  # type: ignore[return-value]


class vectorize:
    """
    Vectorize a call.

    We do not currently support signatures, caching, and none of our functions allow specifying output
    types. All are assumed floats. Specialized methods will be far more performant than using vectorize,
    but vectorize can be quick to use as far as convenience is concerned.

    There is no optimization for small matrices or matrices that are already the same size. This
    assumes worst case: N x M matrices of unknown quantity.
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
        inputs = list(args)

        # Gather all the input values we need to vectorize so we can broadcast them together
        vinputs = [inputs[i] for i in indexes] + [kwargs[k] for k in keys]

        if vinputs:
            # We need to broadcast together the inputs for vectorization.
            # Once vectorized, use the wrapper function to replace each argument
            # with the vectorized iteration. Reshape the output to match the input shape.
            bcast = broadcast(*vinputs)
            m = []
            for vargs in bcast:
                # Update arguments with vectorized arguments
                for e, i in enumerate(indexes):
                    inputs[i] = vargs[e]

                # Update keyword arguments with vectorized keyword argument
                kwargs.update(zip(keys, vargs[size:]))

                # Call the function with vectorized inputs
                m.append(self.func(*inputs, **kwargs))

            # Reshape return to match input shape
            return reshape(m, bcast.shape) if len(bcast.shape) != 1 else m

        # Nothing to vectorize, just run the function with the arguments
        return self.func(*inputs, **kwargs)


class vectorize2:
    """
    A special version of vectorize that only broadcasts the first two inputs.

    This approach is faster than vectorize because it limits the inputs and allows us
    to skip a lot of the generalized code that can slow the things down. Additionally,
    we allow a `dims` keyword that allows you to specify the dimensions of the inputs
    that can fast track a decision on how to process in the inputs.

    By default, `second` enables the expected second numerical input, but this can be set
    to `None` to make it optional or `False` to disable it entirely, making it only accept
    one vectorized input.

    Calls to do not accept arbitrary positional arguments, only one or two depending on
    what how `second` is set. Keyword arguments are allowed, but will not be vectorized.

    For more flexibility, use `vectorize` which allows arbitrary vectorization of any and
    all inputs at the cost of speed.
    """

    def __init__(self, pyfunc: Callable[..., Any], doc: str | None = None, second: bool | None = True):
        """Initialize."""

        self.func = pyfunc
        self.second = second

        # Setup function name and docstring
        self.__name__ = self.func.__name__
        self.__doc__ = self.func.__doc__ if doc is None else doc

    def _vector_apply(self, a: VectorLike, b: VectorLike, **kwargs: Any) -> Vector:
        """Apply a function to two vectors."""

        # Broadcast the vector
        if len(a) == 1:
            a = [a[0]] * len(b)
        elif len(b) == 1:
            b = [b[0]] * len(a)

        return [self.func(x, y, **kwargs) for x, y in zipl(a, b)]

    def __call__(
        self,
        a: ArrayLike | float,
        b: ArrayLike | float,
        *,
        dims: tuple[int, int] | None = None,
        **kwargs: Any
    ) -> Any:
        """Call the vectorized function."""

        if b is None:
            if self.second is False or (self.second is None):
                return reshape([self.func(f, **kwargs) for f in flatiter(a)], shape(a))
            raise ValueError('Function requires 2 positional arguments')

        if not dims or dims[0] > 2 or dims[1] > 2:
            shape_a = shape(a)
            shape_b = shape(b)
            dims_a = len(shape_a)
            dims_b = len(shape_b)

            # Handle matrices of N-D and M-D size
            if dims_a > 2 or dims_b > 2:
                if dims_a == dims_b:
                    # Apply math to two N-D matrices
                    return reshape(
                        [self.func(x, y, **kwargs) for x, y in zip(flatiter(a), flatiter(b))],
                        shape_a
                    )
                elif not dims_a or not dims_b:
                    if not dims_a:
                        # Apply math to a number and an N-D matrix
                        return reshape([self.func(a, x, **kwargs) for x in flatiter(b)], shape_b)
                    # Apply math to an N-D matrix and a number
                    return reshape([self.func(x, b, **kwargs) for x in flatiter(a)], shape_a)

                # Apply math to an N-D matrix and an M-D matrix by broadcasting to a common shape.
                bcast = broadcast(a, b)  # type: ignore[arg-type]
                return reshape([self.func(x, y, **kwargs) for x, y in bcast], bcast.shape)
        else:
            dims_a, dims_b = dims

        # Inputs are of equal size and shape
        if dims_a == dims_b:
            if dims_a == 1:
                # Apply math to two vectors
                return self._vector_apply(a, b, **kwargs)  # type: ignore[arg-type]
            elif dims_a == 2:
                # Apply math to two 2-D matrices
                return [self._vector_apply(ra, rb, **kwargs) for ra, rb in zipl(a, b)]  # type: ignore[arg-type]
            return self.func(a, b, **kwargs)

        # Inputs containing a scalar on either side
        elif not dims_a or not dims_b:
            if dims_a == 1:
                # Apply math to a vector and number
                return [self.func(i, b, **kwargs) for i in a]  # type: ignore[union-attr]
            elif dims_b == 1:
                # Apply math to a number and a vector
                return [self.func(a, i, **kwargs) for i in b]  # type: ignore[union-attr]
            elif dims_a == 2:
                # Apply math to 2-D matrix and number
                return [[self.func(i, b, **kwargs) for i in row] for row in a]  # type: ignore[union-attr]
            # Apply math to a number and a matrix
            return [[self.func(a, i, **kwargs) for i in row] for row in b]  # type: ignore[union-attr]

        # Inputs are at least 2-D dimensions or below on both sides
        if dims_a == 1:
            # Apply math to vector and 2-D matrix
            return [self._vector_apply(a, row, **kwargs) for row in b]  # type: ignore[arg-type, union-attr]
        # Apply math to 2-D matrix and a vector
        return [self._vector_apply(row, b, **kwargs) for row in a]  # type: ignore[arg-type, union-attr]


@overload  # type: ignore[no-overload-impl]
def multiply(a: float, b: float, *, dims: tuple[int, int] | None = None) -> float:  # noqa: D103
    ...


@overload
def multiply(a: float | VectorLike, b: VectorLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def multiply(a: VectorLike, b: float | VectorLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def multiply(a: MatrixLike, b: float | ArrayLike, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


@overload
def multiply(a: ArrayLike | float, b: MatrixLike, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


multiply = vectorize2(operator.mul, doc="Multiply two arrays or floats.")  # type: ignore[assignment]


@overload  # type: ignore[no-overload-impl]
def divide(a: float, b: float, *, dims: tuple[int, int] | None = None) -> float:  # noqa: D103
    ...


@overload
def divide(a: float | VectorLike, b: VectorLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def divide(a: VectorLike, b: float | VectorLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def divide(a: MatrixLike, b: float | ArrayLike, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


@overload
def divide(a: ArrayLike | float, b: MatrixLike, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


divide = vectorize2(operator.truediv, doc="Divide two arrays or floats.")  # type: ignore[assignment]


@overload  # type: ignore[no-overload-impl]
def add(a: float, b: float, *, dims: tuple[int, int] | None = None) -> float:  # noqa: D103
    ...


@overload
def add(a: float | VectorLike, b: VectorLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def add(a: VectorLike, b: float | VectorLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def add(a: MatrixLike, b: float | ArrayLike, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


@overload
def add(a: ArrayLike | float, b: MatrixLike, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


add = vectorize2(operator.add, doc="Add two arrays or floats.")  # type: ignore[assignment]


@overload  # type: ignore[no-overload-impl]
def subtract(a: float, b: float, *, dims: tuple[int, int] | None = None) -> float:  # noqa: D103
    ...


@overload
def subtract(a: float | VectorLike, b: VectorLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def subtract(a: VectorLike, b: float | VectorLike, *, dims: tuple[int, int] | None = None) -> Vector:
    ...


@overload
def subtract(a: MatrixLike, b: float | ArrayLike, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


@overload
def subtract(a: ArrayLike | float, b: MatrixLike, *, dims: tuple[int, int] | None = None) -> Matrix:
    ...


subtract = vectorize2(operator.sub, doc="Subtract two arrays or floats.")  # type: ignore[assignment]


def full(array_shape: int | Sequence[int], fill_value: float | ArrayLike) -> Array:
    """Create and fill a shape with the given values."""

    # Ensure `shape` is a sequence of sizes
    array_shape = tuple([array_shape]) if not isinstance(array_shape, Sequence) else tuple(array_shape)

    # Normalize `fill_value` to be an array.
    if not isinstance(fill_value, Sequence):
        return reshape([fill_value] * prod(array_shape), array_shape)  # type: ignore[return-value]

    # If the shape doesn't fit the data, try and broadcast it.
    # If it does fit, just reshape it.
    if shape(fill_value) != tuple(array_shape):
        return broadcast_to(fill_value, array_shape)
    return reshape(fill_value, array_shape)  # type: ignore[return-value]


def ones(array_shape: int | Sequence[int]) -> Array:
    """Create and fill a shape with ones."""

    return full(array_shape, 1.0)


def zeros(array_shape: int | Sequence[int]) -> Array:
    """Create and fill a shape with zeros."""

    return full(array_shape, 0.0)


def identity(size: int) -> Matrix:
    """Create an identity matrix."""

    return eye(size)


def _flatiter(array: ArrayLike, array_shape: tuple[int, ...]) -> Iterator[float]:
    """Iterate and return values based on shape."""

    nested = len(array_shape) > 1
    for a in array:
        if nested:
            yield from _flatiter(a, array_shape[1:])  # type: ignore[arg-type]
        else:
            yield a  # type: ignore[misc]


def flatiter(array: float | ArrayLike) -> Iterator[float]:
    """Traverse an array returning values."""

    if not isinstance(array, Sequence):
        yield array
    else:
        yield from _flatiter(array, shape(array))


def ravel(array: float | ArrayLike) -> Vector:
    """Return a flattened vector."""

    return list(flatiter(array))


def _frange(start: float, stop: float, step: float) -> Iterator[float]:
    """Float range."""

    x = start
    rev = step < 0.0
    limit = stop - step
    while x >= limit if rev else x <= limit:
        yield x
        x += step


def arange(
    start: SupportsFloatOrInt,
    stop: SupportsFloatOrInt | None = None,
    step: SupportsFloatOrInt = 1
) -> Vector:
    """
    Like arrange, but handles floats as well.

    Return will be a list instead of an iterator.
    Due to floating point precision, floats may be inaccurate to some degree.
    """

    if stop is None:
        stop = start
        start = 0

    if isinstance(start, int) and isinstance(stop, int) and isinstance(step, int):
        return list(range(start, stop, step))
    else:
        return list(_frange(float(start), float(stop), float(step)))


@overload
def transpose(array: VectorLike) -> Vector:
    ...


@overload
def transpose(array: Matrix) -> Matrix:
    ...


def transpose(array: ArrayLike) -> Array:
    """
    A simple transpose of a matrix.

    `numpy` offers the ability to specify different axes, but right now,
    we don't have a need for that, nor the desire to figure it out :).
    """

    s = list(reversed(shape(array)))
    total = prod(s)

    # Create the array
    m = []  # type: Any

    # Calculate data sizes
    dims = len(s)
    length = s[-1]

    # Initialize indexes so we can properly write our data
    idx = [0] * dims

    # Traverse the provided array filling our new array
    for i, v in enumerate(flatiter(array)):

        # Navigate to the proper index to start writing data.
        # If the dimension hasn't been created yet, create it.
        t = m  # type: Any
        for d in range(dims - 1):
            if not t:
                for _ in range(s[d]):
                    t.append([])
            t = t[idx[d]]

        # Initialize the last dimension
        # so we can index at the correct position
        if not t:
            t[:] = [0] * length

        # Write the data
        t[idx[-1]] = v

        # Update the current indexes if we aren't done copying data.
        if i < (total - 1):
            for x in range(dims):
                if (idx[x] + 1) % s[x] == 0:
                    idx[x] = 0
                    x += 1
                else:
                    idx[x] += 1
                    break

    return m  # type: ignore[no-any-return]


def reshape(array: ArrayLike | float, new_shape: int | Sequence[int]) -> float | Array:
    """Change the shape of an array."""

    # Ensure floats are arrays
    if not isinstance(array, Sequence):
        array = [array]

    # Normalize shape specifier to a sequence
    if not isinstance(new_shape, Sequence):
        new_shape = [new_shape]

    # Shape to a scalar
    if not new_shape:
        v = ravel(array)
        if len(v) == 1:
            return v[0]
        else:
            raise ValueError('Shape {} does not match the data total of {}'.format(new_shape, shape(array)))

    # Kick out if the requested shape doesn't match the data
    current_shape = shape(array)

    # Copy the array and quit if we are already the requested shape
    if current_shape == new_shape:
        return acopy(array)

    # Make sure we can actually reshape.
    total = prod(new_shape)
    if total != prod(current_shape):
        raise ValueError('Shape {} does not match the data total of {}'.format(new_shape, shape(array)))

    # Create the array
    m = []  # type: Any

    # Calculate data sizes
    dims = len(new_shape)
    length = new_shape[-1]
    count = int(total // length)

    # Initialize indexes so we can properly write our data
    idx = [0] * (dims - 1)

    # Traverse the provided array filling our new array
    if len(current_shape) > 1:
        data = flatiter(array)
    else:
        data = iter(array)  # type: ignore[arg-type]
    for i in range(count):

        # Navigate to the proper index to start writing data.
        # If the dimension hasn't been created yet, create it.
        t = m  # type: Any
        for d in range(dims - 1):
            if not t:
                for _ in range(new_shape[d]):
                    t.append([])
            t = t[idx[d]]

        # Create the final dimension, writing all the data
        t[:] = [next(data) for _ in range(length)]

        # Update the current indexes if we aren't done copying data.
        if i < (count - 1):
            for x in range(-1, -(dims), -1):
                if idx[x] + 1 == new_shape[x - 1]:
                    idx[x] = 0
                    x += -1
                else:
                    idx[x] += 1
                    break

    return m  # type: ignore[no-any-return]


def _shape(array: ArrayLike, size: int) -> tuple[int, ...]:
    """Iterate the array ensuring that all dimensions are consistent and return the sizes if they are."""

    s = (size,)
    s2 = tuple()  # type: tuple[int, ...]
    size2 = -1
    deeper = True
    for a in array:
        if not isinstance(a, Sequence) or size != len(a):
            raise ValueError('Ragged lists are not supported')
        elif deeper:
            if a and isinstance(a[0], Sequence):
                if size2 < 0:
                    size2 = len(a[0])
                s2 = _shape(a, size2)
            else:
                deeper = False
                s2 = tuple()
    return s + s2 if s2 else s


def shape(array: float | ArrayLike) -> tuple[int, ...]:
    """Get the shape of an array."""

    if isinstance(array, Sequence):
        s = (len(array),)

        # Zero length vector
        if not s[0]:
            return s

        # Handle scalars
        is_scalar = False
        all_scalar = True
        for a in array:
            if not isinstance(a, Sequence):
                is_scalar = True
                if not all_scalar:
                    break
            else:
                all_scalar = False
        if is_scalar:
            if all_scalar:
                return s
            raise ValueError('Ragged lists are not supported')

        # Looks like we only have sequences
        return s + _shape(array, len(array[0]))  # type: ignore[arg-type]
    else:
        # Scalar
        return tuple()


def fill_diagonal(matrix: MatrixLike, val: float | ArrayLike = 0.0, wrap: bool = False) -> None:
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


def eye(n: int, m: int | None = None, k: int = 0) -> Matrix:
    """Create a diagonal of ones in a zero initialized matrix at the specified position."""

    if m is None:
        m = n

    # Length of diagonal
    dlen = m if n > m and k < 0 else (m - abs(k))

    a = []  # type: Matrix
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


@overload
def diag(array: VectorLike, k: int = 0) -> Matrix:
    ...


@overload
def diag(array: MatrixLike, k: int = 0) -> Vector:
    ...


def diag(array: ArrayLike, k: int = 0) -> Array:
    """Create a diagonal matrix from a vector or return a vector of the diagonal of a matrix."""

    s = shape(array)
    dims = len(s)
    if not dims or dims > 2:
        raise ValueError('Array must be 1-D or 2-D in shape')

    if dims == 1:
        # Calculate size of matrix to accommodate the diagonal
        size = s[0] - k if k < 0 else (s[0] + k if k else s[0])
        maximum = size - 1
        minimum = 0

        # Create a diagonal matrix with the provided vector
        m = []  # type: Matrix
        for i in range(size):
            pos = i + k
            idx = i if k >= 0 else pos
            m.append(
                ([0.0] * clamp(pos, minimum, maximum)) +
                [array[idx] if (0 <= pos < size) else 0.0] +  # type: ignore[arg-type]
                ([0.0] * clamp(size - pos - 1, minimum, maximum))
            )
        return m
    else:
        # Extract the requested diagonal from a rectangular 2-D matrix
        size = s[1]
        d = []
        for i, r in enumerate(array):
            pos = i + k
            if (0 <= pos < size):
                d.append(r[pos])  # type: ignore[index]
        return d


def inv(matrix: MatrixLike) -> Matrix:
    """
    Invert the matrix.

    Derived from https://github.com/ThomIves/MatrixInverse.

    This is free and unencumbered software released into the public domain.

    Anyone is free to copy, modify, publish, use, compile, sell, or
    distribute this software, either in source code form or as a compiled
    binary, for any purpose, commercial or non-commercial, and by any
    means.

    In jurisdictions that recognize copyright laws, the author or authors
    of this software dedicate any and all copyright interest in the
    software to the public domain. We make this dedication for the benefit
    of the public at large and to the detriment of our heirs and
    successors. We intend this dedication to be an overt act of
    relinquishment in perpetuity of all present and future rights to this
    software under copyright law.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
    OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

    For more information, please refer to <http://unlicense.org/>

    ---

    Heavily modified by Isaac Muse.

    - Modified to handle greater than 2 x 2 dimensions.
    - Modified to shuffle rows to help handle a valid matrix which has a zero
      at a pivot point.
    """

    # Ensure we have a square matrix
    s = shape(matrix)
    dims = len(s)
    if dims < 2 or min(s) != max(s):
        raise ValueError('Matrix must be a N x N matrix')

    # Handle dimensions greater than 2 x 2
    elif dims > 2:
        invert = []
        cols = list(_extract_dims(matrix, dims, dims - 2))
        for c in cols:
            invert.append(transpose(inv(c)))  # type: ignore[arg-type]
        return reshape(invert, s)  # type: ignore[return-value]

    # Get size and calculate augmented size
    size = s[0]

    # Create the traditional augmented matrix, but keep the identity matrix and original matrix separate.
    m = [list(row) for row in matrix]
    mi = identity(size)

    # Ensure we do not zero values at each pivot point
    for i in range(size):
        # Is pivot point zero?
        if m[i][i] == 0.0:

            # Try to swap with a row where the pivot points in each row are not zero.
            for j in list(range(i + 1, size)) + list(range(i - 1)):
                if m[j][i] != 0.0 and m[i][j] != 0.0:
                    m[i], m[j] = m[j], m[i]
                    mi[i], mi[j] = mi[j], mi[i]
                    break

            # We cannot invert this matrix
            else:
                raise ValueError("Matrix is not invertible")

    for i in range(size):

        # Scale the diagonal such that it will now equal 1
        scalar = 1 / m[i][i]
        for j in range(size):
            m[i][j] *= scalar
            mi[i][j] *= scalar

        # Now, using the value found at the index `i` in the remaining rows (excluding the pivot point `m[i]`),
        # Where `r` is the current row under evaluation, subtract `m[r][i] * m[i] from m[r]`.
        for r in range(size):
            # Skip the pivot point
            if r == i:
                continue

            # The scalar for the current row
            scalar = m[r][i]

            # Scale each item in the row (i) and subtract it from the current row (r)
            for j in range(size):
                m[r][j] -= scalar * m[i][j]
                mi[r][j] -= scalar * mi[i][j]

    # Return the inverse from the right side of the augmented matrix
    return mi


def vstack(arrays: Sequence[ArrayLike]) -> Array:
    """Vertical stack."""

    m = []  # type: list[Any]
    first = True
    dims = 0
    for i in arrays:
        cs = shape(i)
        if first:
            dims = len(cs)
            first = False
            if dims == 0:
                return reshape(arrays, (len(arrays), 1))  # type: ignore[return-value, arg-type]
            elif dims == 1:
                return reshape(arrays, (len(arrays), cs[-1]))  # type: ignore[return-value, arg-type]
        m.extend(reshape(i, (prod(cs[:1 - dims]),) + cs[1 - dims:-1] + cs[-1:]))  # type: ignore[arg-type]

    if first:
        raise ValueError("'vstack' requires at least one array")

    return m


def _hstack_extract(a: ArrayLike, s: Sequence[int]) -> Iterator[Vector]:
    """Extract data from the second dimension."""

    data = flatiter(a)
    length = prod(s[1:])
    for _ in range(s[0]):
        yield [next(data) for _ in range(length)]


def hstack(arrays: Sequence[ArrayLike]) -> Array:
    """Horizontal stack."""

    # Gather up shapes
    columns = 0
    shapes = []
    first = None  # type: tuple[int, ...] | None
    for a in arrays:
        cs = shape(a)

        # Shortcut out for simple list of numbers or 1-D arrays
        if first is None:
            first = cs
            if not cs:
                return reshape(arrays, (len(arrays),))  # type: ignore[return-value, arg-type]
            elif len(cs) == 1:
                m1 = []  # type: Vector
                for a1 in arrays:
                    m1.extend(ravel(a1))
                return reshape(m1, (len(m1),))  # type: ignore[return-value]

        # Gather up shapes and tally the size of the new second dimension
        columns += cs[1]
        shapes.append(cs)

    if first is None:
        raise ValueError("'hstack' requires at least one array")

    # Iterate the arrays returning the content per second dimension
    m = []  # type: list[Any]
    for data in zipl(*[_hstack_extract(a, s) for a, s in zipl(arrays, shapes)]):
        for d in data:
            m.extend(d)

    # Shape the data to the new shape
    new_shape = first[:1] + tuple([columns]) + first[2:]
    return reshape(m, new_shape)  # type: ignore[return-value]


def outer(a: float | ArrayLike, b: float | ArrayLike) -> Matrix:
    """Compute the outer product of two vectors (or flattened matrices)."""

    v1 = ravel(a)
    v2 = ravel(b)
    return [[x * y for y in v2] for x in v1]


def inner(a: float | ArrayLike, b: float | ArrayLike) -> float | Array:
    """Compute the inner product of two arrays."""

    shape_a = shape(a)
    shape_b = shape(b)
    dims_a = len(shape_a)
    dims_b = len(shape_b)

    # If both inputs are not scalars, the last dimension must match
    if (shape_a and shape_b and shape_a[-1] != shape_b[-1]):
        raise ValueError('The last dimensions {} and {} do not match'.format(shape_a, shape_b))

    # If we have a scalar, we should just multiply
    if (not dims_a or not dims_b):
        return multiply(a, b, dims=(dims_a, dims_b))

    # Adjust the input so that they can properly be evaluated
    # Scalars will be broadcasted to properly match the last dimension
    # of the other input.
    if dims_a == 1:
        first = [a]  # type: Any
    elif dims_a > 2:
        first = list(_extract_dims(a, dims_a, dims_a - 1))  # type: ignore[arg-type]
    else:
        first = a

    if dims_b == 1:
        second = [b]  # type: Any
    elif dims_b > 2:
        second = list(_extract_dims(b, dims_b, dims_b - 1))  # type: ignore[arg-type]
    else:
        second = b

    # Perform the actual inner product
    m = [[sum([x * y for x, y in zipl(r1, r2)]) for r2 in second] for r1 in first]
    new_shape = shape_a[:-1] + shape_b[:-1]

    # Shape the data.
    return reshape(m, new_shape)
