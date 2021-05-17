"""Utilities."""
import copy
import math
import numbers
import warnings
from functools import wraps

NaN = float('nan')
INF = float('inf')
ACHROMATIC_THRESHOLD = 0.0005
DEF_PREC = 5
DEF_FIT_TOLERANCE = 0.000075
DEF_ALPHA = 1.0
DEF_MIX = 0.5
DEF_HUE_ADJ = "shorter"
DEF_DISTANCE_SPACE = "lab"
DEF_FIT = "lch-chroma"
DEF_DELTA_E = "76"

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


def pq_st2084_inverse_eotf(values, c1=C1, c2=C2, c3=C3, m1=M1, m2=M2):
    """Perceptual quantizer (SMPTE ST 2084) - inverse EOTF."""

    adjusted = []
    for c in values:
        c = npow(c / 10000, m1)
        r = (c1 + c2 * c) / (1 + c3 * c)
        adjusted.append(npow(r, m2))
    return adjusted


def pq_st2084_eotf(values, c1=C1, c2=C2, c3=C3, m1=M1, m2=M2):
    """Perceptual quantizer (SMPTE ST 2084) - EOTF."""

    im1 = 1 / m1
    im2 = 1 / m2

    adjusted = []
    for c in values:
        c = npow(c, im2)
        r = (c - c1) / (c2 - c3 * c)
        adjusted.append(10000 * npow(r, im1))
    return adjusted


def xyz_d65_to_absxyzd65(xyzd65):
    """XYZ D65 to Absolute XYZ D65."""

    return [max(c * YW, 0) for c in xyzd65]


def absxyzd65_to_xyz_d65(absxyzd65):
    """Absolute XYZ D65 XYZ D65."""

    return [max(c / YW, 0) for c in absxyzd65]


def npow(base, exp):
    """Perform `pow` with a negative number."""

    return math.copysign(abs(base) ** exp, base)


def constrain_hue(hue):
    """Constrain hue to 0 - 360."""

    return hue % 360 if not is_nan(hue) else hue


def is_number(value):
    """Check if value is a number."""

    return isinstance(value, numbers.Number)


def is_nan(value):
    """Check if value is "not a number"."""

    return math.isnan(value)


def no_nan(value):
    """Convert list of numbers or single number to valid numbers."""

    if is_number(value):
        return 0.0 if is_nan(value) else value
    else:
        return [(0.0 if is_nan(x) else x) for x in value]


def cmp_coords(c1, c2):
    """Compare coordinates."""

    if is_number(c1):
        return (math.isnan(c1) and math.isnan(c2)) or c1 == c2
    elif len(c1) != len(c2):
        return False
    else:
        return all(map(lambda a, b: (math.isnan(a) and math.isnan(b)) or a == b, c1, c2))


def dot(a, b):
    """Get dot product of simple numbers, vectors, and 2D matrices and/or numbers."""

    is_a_num = is_number(a)
    is_b_num = is_number(b)
    is_a_vec = not is_a_num and is_number(a[0])
    is_b_vec = not is_b_num and is_number(b[0])
    is_a_mat = not is_a_num and not is_a_vec
    is_b_mat = not is_b_num and not is_b_vec

    if is_a_num or is_b_num:
        # Trying to dot a number with a vector or a matrix, so just multiply
        value = multiply(a, b)
    elif is_a_vec and is_b_vec:
        # Dot product of two vectors
        value = sum([x * y for x, y in zip(a, b)])
    elif is_a_mat and is_b_vec:
        # Dot product of matrix and a vector
        value = [sum([x * y for x, y in zip(row, b)]) for row in a]
    elif is_a_vec and is_b_mat:
        # Dot product of vector and a matrix
        value = [sum([x * y for x, y in zip(a, col)]) for col in zip(*b)]
    else:
        # Dot product of two matrices
        value = [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]

    return value


def multiply(a, b):
    """Multiply simple numbers, vectors, and 2D matrices."""

    is_a_num = is_number(a)
    is_b_num = is_number(b)
    is_a_vec = not is_a_num and is_number(a[0])
    is_b_vec = not is_b_num and is_number(b[0])
    is_a_mat = not is_a_num and not is_a_vec
    is_b_mat = not is_b_num and not is_b_vec

    if is_a_num and is_b_num:
        # Multiply two numbers
        value = a * b
    elif is_a_num and not is_b_num:
        # Multiply a number and vector/matrix
        value = [multiply(a, i) for i in b]
    elif is_b_num and not is_a_num:
        # Multiply a vector/matrix and number
        value = [multiply(i, b) for i in a]
    elif is_a_vec and is_b_vec:
        # Multiply two vectors
        value = [x * y for x, y in zip(a, b)]
    elif is_a_mat and is_b_vec:
        # Multiply matrix and a vector
        value = [[x * y for x, y in zip(row, b)] for row in a]
    elif is_a_vec and is_b_mat:
        # Multiply vector and a matrix
        value = [[x * y for x, y in zip(row, a)] for row in b]
    else:
        # Multiply two matrices
        value = [[x * y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]

    return value


def divide(a, b):
    """Divide simple numbers, vectors, and 2D matrices."""

    is_a_num = isinstance(a, numbers.Number)
    is_b_num = isinstance(b, numbers.Number)
    is_a_vec = not is_a_num and isinstance(a[0], numbers.Number)
    is_b_vec = not is_b_num and isinstance(b[0], numbers.Number)
    is_a_mat = not is_a_num and not is_a_vec
    is_b_mat = not is_b_num and not is_b_vec

    if is_a_num and is_b_num:
        # Divide two numbers
        value = a / b
    elif is_a_num and not is_b_num:
        # Divide a number and vector/matrix
        value = [divide(a, i) for i in b]
    elif is_b_num and not is_a_num:
        # Divide a vector/matrix and number
        value = [divide(i, b) for i in a]
    elif is_a_vec and is_b_vec:
        # Divide two vectors
        value = [x / y for x, y in zip(a, b)]
    elif is_a_mat and is_b_vec:
        # Divide matrix and a vector
        value = [[x / y for x, y in zip(row, b)] for row in a]
    elif is_a_vec and is_b_mat:
        # Divide vector and a matrix
        value = [[x / y for x, y in zip(row, a)] for row in b]
    else:
        # Divide two matrices
        value = [[x / y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]

    return value


def diag(v, k=0):
    """Create a diagonal matrix from a vector or return a vector of the diagonal of a matrix."""

    is_vector = isinstance(v[0], numbers.Number)
    size = len(v)
    d = []

    if is_vector:
        # Create a diagonal matrix with the provided values
        for i, value in enumerate(v):
            # Check that the matrix is square, we .cannot invert the matrix if it is not
            d.append([0] * i + [value] + [0] * (size - i - 1))
    else:  # pragma: no cover
        for r in v:
            if len(r) != size:
                raise ValueError('Matrix must be a n x n matrix')
            if 0 <= k < size:
                d.append(r[k])
            k += 1
    return d


def inv(matrix):
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
    m = copy.deepcopy(matrix)

    # Ensure we have a square matrix
    for r in m:
        if len(r) != size:  # pragma: no cover
            raise ValueError('Matrix must be a n x n matrix')

    # Create an identity matrix of the same size as our provided matrix
    im = diag([1] * size)

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


def cbrt(n):
    """Calculate cube root."""

    return nth_root(n, 3)


def nth_root(n, p):
    """Calculate nth root."""

    if p == 0:  # pragma: no cover
        return float('inf')

    if n == 0:
        # Can't do anything with zero
        return 0

    return math.copysign(abs(n) ** (p ** -1), n)


def clamp(value, mn=None, mx=None):
    """Clamp the value to the the given minimum and maximum."""

    if mn is None and mx is None:
        return value
    elif mn is None:
        return min(value, mx)
    elif mx is None:
        return max(value, mn)
    else:
        return max(min(value, mx), mn)


def fmt_float(f, p=0):
    """
    Set float precision and trim precision zeros.

    0: Round to whole integer
    -1: Full precision
    <positive number>: precision level
    """

    value = adjust_precision(f, p)
    string = ('{{:{}f}}'.format('.53' if p == -1 else '.' + str(p))).format(value)
    return string if value.is_integer() and p == 0 else string.rstrip('0').rstrip('.')


def adjust_precision(f, p=0):
    """Adjust precision."""

    if p == -1:
        return f

    elif p == 0:
        return round_half_up(f)

    else:
        whole = int(f)
        digits = 0 if whole == 0 else int(math.log10(-whole if whole < 0 else whole)) + 1
        return round_half_up(whole if digits >= p else f, p - digits)


def round_half_up(n, scale=0):
    """Round half up."""

    mult = 10 ** scale
    return math.floor(n * mult + 0.5) / mult


def deprecated(message, stacklevel=2):  # pragma: no cover
    """
    Raise a `DeprecationWarning` when wrapped function/method is called.

    Borrowed from https://stackoverflow.com/a/48632082/866026
    """

    def _decorator(func):
        @wraps(func)
        def _func(*args, **kwargs):
            warnings.warn(
                "'{}' is deprecated. {}".format(func.__name__, message),
                category=DeprecationWarning,
                stacklevel=stacklevel
            )
            return func(*args, **kwargs)
        return _func
    return _decorator
