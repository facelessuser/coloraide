"""
Math related methods.

Includes various math related functions to aide in color translation and manipulation.

We actually also implement a number of matrix methods. This is mainly to avoid requiring
all of `numpy` as a dependency. While `numpy` would be faster and more feature rich,
avoiding it keeps our dependencies light.

Often, we will borrow the API interface of `numpy`, but functionality may not be the same.
We will often reduce complexity to handle simple 2D matrices as that is all we ever need
for colors (so far). We will also abandon features if we don't want to figure them out as
we aren't suing them :).
"""
import math
import copy
from .types import Array, Matrix, Vector, MutableArray, MutableMatrix, MutableVector
from typing import Optional, Sequence, List, Union, Iterator, Any, cast

NaN = float('nan')
INF = float('inf')


def is_nan(obj: float) -> bool:
    """Check if "not a number"."""

    return math.isnan(obj)


def round_half_up(n: float, scale: int = 0) -> float:
    """Round half up."""

    mult = 10.0 ** scale
    return math.floor(n * mult + 0.5) / mult


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


def _vector_dot(a: Vector, b: Vector) -> float:
    """Dot two vectors."""

    return sum([x * y for x, y in zip(a, b)])


def _vector_div(a: Vector, b: Vector) -> MutableVector:
    """Divide two vectors."""

    if len(a) == 1:
        a = [a[0]] * len(b)
    elif len(b) == 1:
        b = [b[0]] * len(a)

    return [x / y for x, y in zip(a, b)]


def _vector_mult(a: Vector, b: Vector) -> MutableVector:
    """Multiply two vectors."""

    if len(a) == 1:
        a = [a[0]] * len(b)
    elif len(b) == 1:
        b = [b[0]] * len(a)

    return [x * y for x, y in zip(a, b)]


def _extract_dimension(
    m: Array,
    target: int,
    depth: int = 0
) -> Iterator[Array]:
    """Extract the requested dimension."""

    if depth == target:
        if isinstance(m[0], Sequence):
            yield cast(Array, [[cast(Array, x)[r] for x in m] for r in range(len(m[0]))])
        else:
            yield m
    else:
        for m2 in m:
            yield from cast(Array, _extract_dimension(cast(Array, m2), target, depth + 1))


def dot(a: Union[float, Array], b: Union[float, Array]) -> Union[float, MutableArray]:
    """Get dot product of simple numbers, vectors, and matrices."""

    shape_a = shape(a)
    shape_b = shape(b)
    dims_a = len(shape_a)
    dims_b = len(shape_b)

    # Avoid matrices of incompatible shapes
    if dims_a and dims_b:
        if dims_a == 1 and dims_b == 1:
            if shape_a[-1] != shape_b[-1]:
                raise ValueError('Cannot dot vectors of size {} and {}'.format(shape_a, shape_b))
        elif dims_a == 1:
            if shape_a[-1] != shape_b[-2]:
                raise ValueError('Cannot dot vector and matrix of shape {} and {}'.format(shape_a, shape_b))
        elif dims_b == 1:
            if shape_a[-1] != shape_b[-1]:
                raise ValueError('Cannot dot matrix and vector of shape {} and {}'.format(shape_a, shape_b))
        elif shape_a[-1] != shape_b[-2]:
            raise ValueError('Cannot dot matrices of shape {} and {}'.format(shape_a, shape_b))

    if dims_a == 1:
        if dims_b == 1:
            # Dot product of two vectors
            return _vector_dot(cast(Vector, a), cast(Vector, b))
        elif dims_b == 2:
            # Dot product of vector and a matrix
            return [_vector_dot(cast(Vector, a), col) for col in zip(*cast(Matrix, b))]
        elif dims_b > 2:
            # Dot product of vector and a M-D matrix
            columns1 = list(_extract_dimension(cast(Matrix, b), dims_b - 2))
            shape_c = shape_b[:-2] + shape_b[-1:]
            return reshape([[_vector_dot(cast(Vector, a), cast(Vector, c)) for c in col] for col in columns1], shape_c)

    elif dims_a == 2:
        if dims_b == 1:
            # Dot product of matrix and a vector
            return [_vector_dot(row, cast(Vector, b)) for row in cast(Matrix, a)]
        elif dims_b == 2:
            # Dot product of two matrices
            return cast(
                MutableMatrix,
                [[_vector_dot(row, col) for col in zip(*cast(Matrix, b))] for row in cast(Matrix, a)]
            )
        elif dims_b > 2:
            raise ValueError('Cannot dot matrix of shape {} and {}'.format(dims_a, dims_b))

    elif dims_a > 2:
        # Dot product of N-D and M-D matrices
        # Resultant size: `dot(xy, yz) = xz` or `dot(nxy, myz) = nxmz`
        columns2 = list(_extract_dimension(cast(Array, b), dims_b - 2)) if dims_b > 1 else cast(Array, [[b]])
        rows = list(_extract_dimension(cast(Array, a), dims_a - 1))
        m2 = [
            [[sum(cast(List[float], multiply(row, c))) for c in cast(Vector, col)] for col in columns2]
            for row in rows
        ]
        shape_c = shape_a[:-1]
        if dims_b != 1:
            shape_c += shape_b[:-2] + shape_b[-1:]
        return reshape(cast(MutableArray, m2), shape_c)

    # Trying to dot a number with a vector or a matrix, so just multiply
    return multiply(a, b)


def multiply(a: Union[float, Array], b: Union[float, Array]) -> Union[float, MutableArray]:
    """Multiply simple numbers, vectors, and matrices."""

    shape_a = shape(a)
    shape_b = shape(b)
    dims_a = len(shape_a)
    dims_b = len(shape_b)

    if dims_a == 1:
        if dims_b == 1:
            # Multiply two vectors
            return _vector_mult(cast(Vector, a), cast(Vector, b))
        elif dims_b == 2:
            # Multiply vector and 2D matrix
            return cast(MutableMatrix, [_vector_mult(row, cast(Vector, a)) for row in cast(Matrix, b)])
        elif dims_b > 2:
            # Multiply vector and a M-D matrix
            return cast(MutableMatrix, [multiply(row, cast(Vector, a)) for row in cast(Matrix, b)])
        # Multiply a vector and a number
        return cast(MutableVector, [i * cast(float, b) for i in cast(Vector, a)])

    elif dims_a == 2:
        if dims_b == 1:
            # Multiply 2D matrix and a vector
            return cast(MutableMatrix, [_vector_mult(row, cast(Vector, b)) for row in cast(Matrix, a)])
        elif dims_b == 2:
            # Multiply two 2D matrices
            return cast(MutableMatrix, [_vector_mult(ra, rb) for ra, rb in zip(cast(Matrix, a), cast(Matrix, b))])
        elif dims_b > 2:
            # Multiply a N-D matrix and M-D matrix
            return cast(MutableMatrix, [multiply(ra, rb) for ra, rb in zip(cast(Matrix, a), cast(Matrix, b))])
        # Multiply 2D matrix and a number
        return cast(MutableVector, [[i * cast(float, b) for i in row] for row in cast(Matrix, a)])

    elif dims_a > 2:
        if dims_b == 1:
            # Multiply matrix and a vector
            return cast(MutableMatrix, [multiply(row, cast(Vector, b)) for row in cast(Matrix, a)])
        elif dims_b > 1:
            # Multiply a N-D matrix and M-D matrix
            return cast(MutableMatrix, [multiply(ra, rb) for ra, rb in zip(cast(Matrix, a), cast(Matrix, b))])
        # Multiply a matrix and a number
        return cast(MutableVector, [multiply(row, cast(float, b)) for row in cast(Matrix, a)])

    if dims_b == 1:
        # Multiply a number and a vector
        return cast(MutableVector, [cast(float, a) * i for i in cast(Vector, b)])
    elif dims_b == 2:
        # Multiply a number and a matrix
        return cast(MutableVector, [[cast(float, a) * i for i in row] for row in cast(Matrix, b)])
    elif dims_b > 2:
        # Multiply N-D matrix and M-D matrix
        return cast(MutableVector, [multiply(cast(float, a), row) for row in cast(Matrix, b)])

    # Multiply two numbers
    return cast(float, a) * cast(float, b)


def divide(a: Union[float, Array], b: Union[float, Array]) -> Union[float, Array]:
    """Divide simple numbers, vectors, and 2D matrices."""

    shape_a = shape(a)
    shape_b = shape(b)
    dims_a = len(shape_a)
    dims_b = len(shape_b)

    if dims_a == 1:
        if dims_b == 1:
            # Divide two vectors
            return _vector_div(cast(Vector, a), cast(Vector, b))
        elif dims_b == 2:
            # Divide vector and 2D matrix
            return cast(MutableMatrix, [_vector_div(cast(Vector, a), row) for row in cast(Matrix, b)])
        elif dims_b > 2:
            # Divide vector and N-D matrix
            return cast(MutableMatrix, [divide(cast(Vector, a), row) for row in cast(Matrix, b)])
        # Divide a vector and number
        return cast(MutableVector, [i / cast(float, b) for i in cast(Vector, a)])

    elif dims_a == 2:
        if dims_b == 1:
            # Divide 2D matrix and a vector
            return cast(MutableMatrix, [_vector_div(row, cast(Vector, b)) for row in cast(Matrix, a)])
        elif dims_b == 2:
            # Divide two 2D matrices
            return cast(MutableMatrix, [_vector_div(ra, rb) for ra, rb in zip(cast(Matrix, a), cast(Matrix, b))])
        elif dims_b > 2:
            return cast(MutableMatrix, [divide(ra, rb) for ra, rb in zip(cast(Matrix, a), cast(Matrix, b))])
        # Divide 2D matrix and number
        return cast(MutableVector, [[i / cast(float, b) for i in row] for row in cast(Matrix, a)])

    elif dims_a > 2:
        if dims_b == 1:
            # Divide matrix and a vector
            return cast(MutableMatrix, [divide(row, cast(Vector, b)) for row in cast(Matrix, a)])
        elif dims_b > 1:
            # Divide a N-D matrix and M-D matrix
            return cast(MutableMatrix, [divide(ra, rb) for ra, rb in zip(cast(Matrix, a), cast(Matrix, b))])
        # Divide N-D matrix and a number
        return cast(MutableVector, [divide(row, cast(float, b)) for row in cast(Matrix, a)])

    if dims_b == 1:
        # Divide a number and a vector
        return cast(MutableVector, [cast(float, a) / i for i in cast(Vector, b)])
    elif dims_b == 2:
        # Divide a number and a matrix
        return cast(MutableVector, [[cast(float, a) / i for i in row] for row in cast(Matrix, b)])
    elif dims_b > 2:
        # Divide N-D matrix and M-D matrix
        return cast(MutableVector, [divide(cast(float, a), row) for row in cast(Matrix, b)])

    # Divide two numbers
    return cast(float, a) / cast(float, b)


def full(array_shape: Union[int, Sequence[int]], fill_value: Union[float, MutableArray]) -> MutableArray:
    """Create and fill a shape with the given values."""

    # Ensure `shape` is a sequence of sizes
    array_shape = [array_shape] if not isinstance(array_shape, Sequence) else array_shape

    # Ensure `fill_value` is a sequence of values.
    if not isinstance(fill_value, Sequence):
        fill_value = [fill_value]

    # If the first item is not a sequence, process the row as values for the current dimension.
    length = len(fill_value)
    if not isinstance(fill_value[0], Sequence):
        # Check that the length of this dimension matches the shape or is one,
        # one will expand to fill the dimension.
        if length not in (1, array_shape[0]):
            raise ValueError("Could not adjust input of {} to fit shape of {}".format(fill_value, array_shape))
        if len(array_shape) == 1:
            m = [cast(Vector, fill_value[0])] * array_shape[0] if length == 1 else cast(Vector, fill_value[:])
        else:
            # We have deeper dimensions to fill?
            m = [full(array_shape[1:], fill_value)]
            for _ in range(array_shape[0] - 1):
                m.append(copy.deepcopy(m[0]))

    # Input was nested, so the shape must be multi-dimensional
    elif len(array_shape) > 1:
        m = [full(array_shape[1:], i) for i in fill_value]

    # We had a 1D shape, but a multi-dimensional input
    else:
        raise ValueError("Could not adjust input of {} to fit shape of {}".format(fill_value, array_shape))

    return cast(MutableMatrix, m)


def ones(array_shape: Union[int, Sequence[int]]) -> MutableArray:
    """Create and fill a shape with ones."""

    return full(array_shape, 1.0)


def zeros(array_shape: Union[int, Sequence[int]]) -> MutableArray:
    """Create and fill a shape with zeros."""

    return full(array_shape, 0.0)


def identity(size: int) -> MutableMatrix:
    """Create an identity matrix."""

    return cast(MutableMatrix, diag([1.0] * size))


def flatiter(array: Array) -> Iterator[float]:
    """Traverse an array returning values."""

    for v in array:
        if isinstance(v, Sequence):
            yield from flatiter(v)
        else:
            yield v


def reshape(array: Array, new_shape: Union[int, Sequence[int]]) -> MutableArray:
    """Change the shape of an array."""

    # Normalize shape specifier to a sequence
    if not isinstance(new_shape, Sequence):
        new_shape = [new_shape]

    # Kick out if the requested shape doesn't match the data
    total = math.prod(cast(Iterator[int], new_shape))
    if total != math.prod(shape(array)):
        raise ValueError('Shape {} does not match the data'.format(new_shape))

    dims = len(new_shape)
    idx = [0] * dims

    # Create a zero initilized array with the specified shape
    m = zeros(new_shape)

    # Traverse the provided array filling our new array
    for i, v in enumerate(flatiter(array), 0):
        if i == total:
            raise ValueError('Size of data incompatible with requested shape')
        t = m  # type: Any
        for x in range(dims - 1):
            t = cast(MutableArray, t[idx[x]])
        t[idx[-1]] = v

        if i < total - 1:
            for x in range(-1, -(dims + 1), -1):
                if idx[x] + 1 == new_shape[x]:
                    idx[x] = 0
                    x += -1
                else:
                    idx[x] += 1
                    break

    return m


def shape(array: Union[float, Array]) -> List[int]:
    """Get the shape of an array."""

    s = []
    t = array
    while True:
        if not isinstance(t, Sequence):
            break
        s.append(len(t))
        t = cast(Array, t[0])
    return s


def transpose(array: Array) -> MutableArray:
    """
    A simple transpose of a matrix.

    `numpy` offers the ability to specify diffrent axes, but right now,
    we don't have a need for that, nor the desire to figure it out :).
    """

    s = list(reversed(shape(array)))
    total = math.prod(cast(Iterator[int], s))

    # Create a new zero initialized matrix with the same shape as the provided one.
    m = zeros(s)
    dims = len(s)
    idx = [0] * dims

    for i, v in enumerate(flatiter(array), 0):
        if i == total:
            raise ValueError('Size of data incompatible with requested shape')
        t = m  # type: Any
        for x in range(dims - 1):
            t = cast(MutableArray, t[idx[x]])
        t[idx[-1]] = v

        if i < total - 1:
            for x in range(dims):
                if (idx[x] + 1) % s[x] == 0:
                    idx[x] = 0
                    x += 1
                else:
                    idx[x] += 1
                    break
    return m


def fill_diagonal(matrix: MutableMatrix, val: Union[float, Array] = 0.0, wrap: bool = False) -> None:
    """Fill an N-D matrix diagonal."""

    s = shape(matrix)
    if len(s) < 2:
        raise ValueError('Arrays must be 2D or greater')
    if len(s) != 2:
        wrap = False
        if min(s) != max(s):
            raise ValueError('Arrays larger than 2D must have all dimensions of equal length')

    val = [val] if not isinstance(val, Sequence) else list(flatiter(val))
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


def diag(array: Array, k: int = 0) -> MutableArray:
    """Create a diagonal matrix from a vector or return a vector of the diagonal of a matrix."""

    size = len(array)

    if not isinstance(array[0], Sequence):
        m = []  # type: MutableMatrix
        # Create a diagonal matrix with the provided vector
        for i, value in enumerate(cast(Vector, array)):
            m.append(([0.0] * i) + [value] + ([0.0] * (size - i - 1)))
        return m
    else:  # pragma: no cover
        d = []  # type: MutableVector
        for r in cast(Matrix, array):
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
