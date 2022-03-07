"""Utilities."""
import math
import numbers
import warnings
from functools import wraps
from typing import Optional, Sequence, List, Union, Any, Callable, Mapping, cast, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color

Vector = Sequence[float]
Matrix = Sequence[Sequence[float]]
MutableVector = List[float]
MutableMatrix = List[List[float]]
ColorInput = Union['Color', str, Mapping[str, Any]]

NaN = float('nan')
INF = float('inf')
ACHROMATIC_THRESHOLD = 0.0005
DEF_PREC = 5
DEF_FIT_TOLERANCE = 0.000075
DEF_ALPHA = 1.0
DEF_MIX = 0.5
DEF_HUE_ADJ = "shorter"
DEF_INTERPOLATE = "oklab"
DEF_FIT = "lch-chroma"
DEF_DELTA_E = "76"

ERR_MAP_MSG = """
    To add or remove items from this mapping, please subclass the
    'Color' object and replace the entire mapping by either copying
    this mapping and then altering it or by creating an entirely
    new mapping. Example:

    class MyNewClass(Color):
        {name} = {{**Color.{name}, **my_override_map}}
"""

# Many libraries use 200, but `Colorjs.io` uses 203
# The author explains why 203 was chosen:
#
#   Maximum luminance in PQ is 10,000 cd/m^2
#   Relative XYZ has Y=1 for media white
#   BT.2048 says media white Y=203 at PQ 58
#
# We will currently use 203 for now as the difference is minimal.
# If there were a significant difference, and one clearly gave
# better results, that would make the decision easier, but the
# explanation above seems sufficient for now.
YW = 203

# PQ Constants
# https://en.wikipedia.org/wiki/High-dynamic-range_video#Perceptual_quantizer
M1 = 2610 / 16384
M2 = 2523 / 32
C1 = 3424 / 4096
C2 = 2413 / 128
C3 = 2392 / 128


def xy_to_xyz(xy: Vector, Y: float = 1) -> MutableVector:
    """Convert `xyY` to `xyz`."""

    x, y = xy
    return [0, 0, 0] if y == 0 else [(x * Y) / y, Y, (1 - x - y) * Y / y]


def xyz_to_uv(xyz: Vector) -> MutableVector:
    """XYZ to UV."""

    x, y, z = xyz
    denom = (x + 15 * y + 3 * z)
    if denom != 0:
        u = (4 * x) / denom
        v = (9 * y) / denom
    else:
        u = v = 0

    return [u, v]


def uv_to_xy(uv: Vector) -> MutableVector:
    """XYZ to UV."""

    u, v = uv
    denom = (6 * u - 16 * v + 12)
    if denom != 0:
        x = (9 * u) / denom
        y = (4 * v) / denom
    else:
        x = y = 0

    return [x, y]


def xy_to_uv_1960(xy: Vector) -> MutableVector:
    """XYZ to UV."""

    x, y = xy
    denom = (12 * y - 2 * x + 3)
    if denom != 0:
        u = (4 * x) / denom
        v = (6 * y) / denom
    else:
        u = v = 0

    return [u, v]


def uv_1960_to_xy(uv: Vector) -> MutableVector:
    """XYZ to UV."""

    u, v = uv
    denom = (2 * u - 8 * v + 4)
    if denom != 0:
        x = (3 * u) / denom
        y = (2 * v) / denom
    else:
        x = y = 0

    return [x, y]


def xyz_to_xyY(xyz: Vector, white: Vector) -> MutableVector:
    """XYZ to `xyY`."""

    x, y, z = xyz
    d = x + y + z
    return [white[0], white[1], y] if d == 0 else [x / d, y / d, y]


def pq_st2084_inverse_eotf(
    values: Vector,
    c1: float = C1,
    c2: float = C2,
    c3: float = C3,
    m1: float = M1,
    m2: float = M2
) -> MutableVector:
    """Perceptual quantizer (SMPTE ST 2084) - inverse EOTF."""

    adjusted = []
    for c in values:
        c = npow(c / 10000, m1)
        r = (c1 + c2 * c) / (1 + c3 * c)
        adjusted.append(npow(r, m2))
    return adjusted


def pq_st2084_eotf(
    values: Vector,
    c1: float = C1,
    c2: float = C2,
    c3: float = C3,
    m1: float = M1,
    m2: float = M2
) -> MutableVector:
    """Perceptual quantizer (SMPTE ST 2084) - EOTF."""

    im1 = 1 / m1
    im2 = 1 / m2

    adjusted = []
    for c in values:
        c = npow(c, im2)
        r = (c - c1) / (c2 - c3 * c)
        adjusted.append(10000 * npow(r, im1))
    return adjusted


def xyz_d65_to_absxyzd65(xyzd65: Vector) -> MutableVector:
    """XYZ D65 to Absolute XYZ D65."""

    return [max(c * YW, 0) for c in xyzd65]


def absxyzd65_to_xyz_d65(absxyzd65: Vector) -> MutableVector:
    """Absolute XYZ D65 XYZ D65."""

    return [max(c / YW, 0) for c in absxyzd65]


def npow(base: float, exp: float) -> float:
    """Perform `pow` with a negative number."""

    return math.copysign(abs(base) ** exp, base)


def constrain_hue(hue: float) -> float:
    """Constrain hue to 0 - 360."""

    return hue % 360 if not is_nan(hue) else hue


def is_number(value: Any) -> bool:
    """Check if value is a number."""

    return isinstance(value, numbers.Number)


def is_nan(value: float) -> bool:
    """Check if value is "not a number"."""

    return math.isnan(value)


def no_nans(value: Vector, default: float = 0.0) -> MutableVector:
    """Ensure there are no `NaN` values in a sequence."""

    return [(default if is_nan(x) else x) for x in value]


def no_nan(value: float, default: float = 0.0) -> float:
    """Convert list of numbers or single number to valid numbers."""

    return default if is_nan(value) else value


def cmp_coords(c1: Vector, c2: Vector) -> bool:
    """Compare coordinates."""

    if len(c1) != len(c2):
        return False
    else:
        return all(map(lambda a, b: (math.isnan(a) and math.isnan(b)) or a == b, c1, c2))


def dot(a: Union[float, Vector, Matrix], b: Union[float, Vector, Matrix]) -> Union[float, MutableVector, MutableMatrix]:
    """Get dot product of simple numbers, vectors, and 2D matrices and/or numbers."""

    is_a_num = is_number(a)
    is_b_num = is_number(b)
    is_a_vec = not is_a_num and is_number(cast(Union[Vector, Matrix], a)[0])
    is_b_vec = not is_b_num and is_number(cast(Union[Vector, Matrix], b)[0])
    is_a_mat = not is_a_num and not is_a_vec
    is_b_mat = not is_b_num and not is_b_vec

    if is_a_num or is_b_num:
        # Trying to dot a number with a vector or a matrix, so just multiply
        return multiply(cast(float, a), cast(float, b))
    elif is_a_vec and is_b_vec:
        # Dot product of two vectors
        return sum([x * y for x, y in zip(cast(Vector, a), cast(Vector, b))])
    elif is_a_mat and is_b_vec:
        # Dot product of matrix and a vector
        return [sum([x * y for x, y in zip(row, cast(Vector, b))]) for row in cast(Matrix, a)]
    elif is_a_vec and is_b_mat:
        # Dot product of vector and a matrix
        return [sum([x * y for x, y in zip(cast(Vector, a), col)]) for col in zip(*cast(Matrix, b))]
    else:
        # Dot product of two matrices
        return cast(
            MutableMatrix,
            [[sum(x * y for x, y in zip(row, col)) for col in zip(*cast(Matrix, b))] for row in cast(Matrix, a)]
        )


def multiply(
    a: Union[float, Vector, Matrix],
    b: Union[float, Vector, Matrix]
) -> Union[float, MutableVector, MutableMatrix]:
    """Multiply simple numbers, vectors, and 2D matrices."""

    is_a_num = is_number(a)
    is_b_num = is_number(b)
    is_a_vec = not is_a_num and is_number(cast(Union[Vector, Matrix], a)[0])
    is_b_vec = not is_b_num and is_number(cast(Union[Vector, Matrix], b)[0])
    is_a_mat = not is_a_num and not is_a_vec
    is_b_mat = not is_b_num and not is_b_vec

    if is_a_num and is_b_num:
        # Multiply two numbers
        return cast(float, a) * cast(float, b)
    elif is_a_num and not is_b_num:
        # Multiply a number and vector/matrix
        return cast(MutableVector, [multiply(cast(float, a), i) for i in cast(Union[Vector, Matrix], b)])
    elif is_b_num and not is_a_num:
        # Multiply a vector/matrix and number
        return cast(MutableVector, [multiply(i, cast(float, b)) for i in cast(Union[Vector, Matrix], a)])
    elif is_a_vec and is_b_vec:
        # Multiply two vectors
        return cast(MutableVector, [x * y for x, y in zip(cast(Vector, a), cast(Vector, b))])
    elif is_a_mat and is_b_vec:
        # Multiply matrix and a vector
        return cast(MutableMatrix, [[x * y for x, y in zip(row, cast(Vector, b))] for row in cast(Matrix, a)])
    elif is_a_vec and is_b_mat:
        # Multiply vector and a matrix
        return cast(MutableMatrix, [[x * y for x, y in zip(row, cast(Vector, a))] for row in cast(Matrix, b)])
    else:
        # Multiply two matrices
        return cast(
            MutableMatrix,
            [[x * y for x, y in zip(ra, rb)] for ra, rb in zip(cast(Matrix, a), cast(Matrix, b))]
        )


def divide(
    a: Union[float, Vector, Matrix],
    b: Union[float, Vector, Matrix]
) -> Union[float, MutableVector, MutableMatrix]:
    """Divide simple numbers, vectors, and 2D matrices."""

    is_a_num = is_number(a)
    is_b_num = is_number(b)
    is_a_vec = not is_a_num and is_number(cast(Union[Vector, Matrix], a)[0])
    is_b_vec = not is_b_num and is_number(cast(Union[Vector, Matrix], b)[0])
    is_a_mat = not is_a_num and not is_a_vec
    is_b_mat = not is_b_num and not is_b_vec

    if is_a_num and is_b_num:
        # Divide two numbers
        return cast(float, a) / cast(float, b)
    elif is_a_num and not is_b_num:
        # Divide a number and vector/matrix
        return cast(MutableVector, [divide(cast(float, a), i) for i in cast(Union[Vector, Matrix], b)])
    elif is_b_num and not is_a_num:
        # Divide a vector/matrix and number
        return cast(MutableVector, [divide(i, cast(float, b)) for i in cast(Union[Vector, Matrix], a)])
    elif is_a_vec and is_b_vec:
        # Divide two vectors
        return cast(MutableVector, [x / y for x, y in zip(cast(Vector, a), cast(Vector, b))])
    elif is_a_mat and is_b_vec:
        # Divide matrix and a vector
        return cast(MutableMatrix, [[x / y for x, y in zip(row, cast(Vector, b))] for row in cast(Matrix, a)])
    elif is_a_vec and is_b_mat:
        # Divide vector and a matrix
        return cast(MutableMatrix, [[x / y for x, y in zip(row, cast(Vector, a))] for row in cast(Matrix, b)])
    else:
        # Divide two matrices
        return cast(
            MutableMatrix,
            [[x / y for x, y in zip(ra, rb)] for ra, rb in zip(cast(Matrix, a), cast(Matrix, b))]
        )


def diag(v: Union[Vector, Matrix], k: int = 0) -> Union[MutableVector, MutableMatrix]:
    """Create a diagonal matrix from a vector or return a vector of the diagonal of a matrix."""

    size = len(v)

    if isinstance(v[0], numbers.Number):
        m = []  # type: MutableMatrix
        # Create a diagonal matrix with the provided vector
        for i, value in enumerate(cast(Vector, v)):
            m.append(([0.0] * i) + [value] + ([0.0] * (size - i - 1)))
        return m
    else:  # pragma: no cover
        d = []  # type: MutableVector
        for r in cast(Matrix, v):
            # Check that the matrix is square
            if len(r) != size:
                raise ValueError('Matrix must be a n x n matrix')
            # Return just the specified diagonal vector
            if 0 <= k < size:
                d.append(r[k])
            k += 1
        return d


def inv(matrix: Matrix) -> MutableMatrix:
    """
    Invert the matrix.

    Derived from https://github.com/ThomIves/MatrixInverse.

    While not as performant as using `numpy`, we are often caching any
    inversion we are doing, so this keeps us from having to require all
    of `numpy` for the few hits to this we do.

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
    """

    size = len(matrix)
    indices = list(range(size))
    m = [list(x) for x in matrix]

    # Ensure we have a square matrix
    for r in m:
        if len(r) != size:  # pragma: no cover
            raise ValueError('Matrix must be a n x n matrix')

    # Create an identity matrix of the same size as our provided vector
    im = cast(List[List[float]], diag([1] * size))

    # Iterating through each row, we will scale each row by it's "focus diagonal".
    # Then using the scaled row, we will adjust the other rows.
    # ```
    # [[fd, 0,  0 ]
    #  [0,  fd, 0 ]
    #  [0,  0,  fd]]
    # ```
    for fd in indices:
        # We will divide each value in the row by the "focus diagonal" value.
        # If the we have a zero for the given `fd` value, we cannot invert.
        denom = m[fd][fd]
        if denom == 0:  # pragma: no cover
            raise ValueError('Matrix is not invertable')

        # We are converting the matrix to the identity and vice versa,
        # So scale the diagonal such that it will now equal 1.
        # Additionally, the same operations will be applied to the identity matrix
        # and will turn it into `m ** -1` (what we are looking for)
        fd_scalar = 1.0 / denom
        for j in indices:
            m[fd][j] *= fd_scalar
            im[fd][j] *= fd_scalar

        # Now, using the value found at the index `fd` in the remaining rows (excluding `row[fd]`),
        # Where `cr` is the current row under evaluation, subtract `row[cr][fd] * row[fd] from row[cr]`.
        for cr in indices[0:fd] + indices[fd + 1:]:
            # The scalar for the current row
            cr_scalar = m[cr][fd]

            # Scale each item in the `row[fd]` and subtract it from the current row `row[cr]`
            for j in indices:
                m[cr][j] -= cr_scalar * m[fd][j]
                im[cr][j] -= cr_scalar * im[fd][j]

    # The identify matrix is now the inverse matrix and vice versa.
    return im


def cbrt(n: float) -> float:
    """Calculate cube root."""

    return nth_root(n, 3)


def nth_root(n: float, p: float) -> float:
    """Calculate nth root."""

    if p == 0:  # pragma: no cover
        return float('inf')

    if n == 0:
        # Can't do anything with zero
        return 0

    return math.copysign(abs(n) ** (p ** -1), n)


def clamp(value: float, mn: Optional[float] = None, mx: Optional[float] = None) -> float:
    """Clamp the value to the the given minimum and maximum."""

    if mn is not None and mx is not None:
        return max(min(value, mx), mn)
    elif mn is not None:
        return max(value, mn)
    elif mx is not None:
        return min(value, mx)
    else:
        return value


def fmt_float(f: float, p: int = 0) -> str:
    """
    Set float precision and trim precision zeros.

    0: Round to whole integer
    -1: Full precision
    <positive number>: precision level
    """

    if is_nan(f):
        return "none"

    value = adjust_precision(f, p)
    string = ('{{:{}f}}'.format('.53' if p == -1 else '.' + str(p))).format(value)
    return string if value.is_integer() and p == 0 else string.rstrip('0').rstrip('.')


def fmt_percent(f: float, p: int = 0) -> str:
    """Get percent."""

    if not is_nan(f):
        value = '{}%'.format(fmt_float(f, p))
    else:
        value = 'none'
    return value


def adjust_precision(f: float, p: int = 0) -> float:
    """Adjust precision."""

    if p == -1:
        return f

    elif p == 0:
        return round_half_up(f)

    else:
        whole = int(f)
        digits = 0 if whole == 0 else int(math.log10(-whole if whole < 0 else whole)) + 1
        return round_half_up(whole if digits > p else f, p - digits)


def round_half_up(n: float, scale: int = 0) -> float:
    """Round half up."""

    mult = 10.0 ** scale
    return math.floor(n * mult + 0.5) / mult


def deprecated(message: str, stacklevel: int = 2) -> Callable[..., Any]:  # pragma: no cover
    """
    Raise a `DeprecationWarning` when wrapped function/method is called.

    Usage:

        @deprecated("This method will be removed in version X; use Y instead.")
        def some_method()"
            pass
    """

    def _wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def _deprecated_func(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                "'{}' is deprecated. {}".format(func.__name__, message),
                category=DeprecationWarning,
                stacklevel=stacklevel
            )
            return func(*args, **kwargs)
        return _deprecated_func
    return _wrapper


def warn_deprecated(message: str, stacklevel: int = 2) -> None:  # pragma: no cover
    """Warn deprecated."""

    warnings.warn(
        message,
        category=DeprecationWarning,
        stacklevel=stacklevel
    )
