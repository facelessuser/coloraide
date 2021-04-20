"""Utilities."""
import decimal
import math
import numbers
import re
import warnings
from functools import wraps

RE_FLOAT_TRIM = re.compile(r'^(?P<keep>-?\d+)(?P<trash>\.0+|(?P<keep2>\.\d*[1-9])0+)$')
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
    """Print is "not a number"."""

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


def cbrt(x):
    """Cube root."""

    if 0 <= x:
        return x ** (1.0 / 3.0)
    return -(-x) ** (1.0 / 3.0)


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


def adjust_precision(f, p):
    """Adjust precision and scale."""

    with decimal.localcontext() as ctx:
        if p > 0:
            # Set precision
            ctx.prec = p
        ctx.rounding = decimal.ROUND_HALF_UP

        if p == -1:
            # Full precision
            value = decimal.Decimal(f)
        elif p == 0:
            # Just round to integer
            value = decimal.Decimal(round_half_up(f))
        else:
            # Round to precision
            value = (decimal.Decimal(f) * decimal.Decimal('1.0'))
            exp = value.as_tuple().exponent
            if exp < 0 and abs(value.as_tuple().exponent) > p:
                value = value.quantize(decimal.Decimal(10) ** -p)

        if value.is_zero():
            value = abs(value)

        return float(value)


def fmt_float(f, p=0):
    """
    Set float precision and trim precision zeros.

    0: Round to whole integer
    -1: Full precision
    <positive number>: precision level
    """

    value = adjust_precision(f, p)
    string = ('{{:{}f}}'.format('.53' if p == -1 else '.' + str(p))).format(value)
    m = RE_FLOAT_TRIM.match(string)
    if m:
        string = m.group('keep')
        if m.group('keep2'):
            string += m.group('keep2')
    return string


def round_half_up(n, scale=0):
    """Round half up."""

    if scale == -1:
        return n

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
