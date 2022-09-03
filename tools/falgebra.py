"""Algebra overrides to ensure fractions support"""
from fractions import Fraction
import os
import sys

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from coloraide import algebra as alg  # noqa: E402

__all__ = ('dot', 'transpose', 'diag', 'inv', 'multiply', 'divide', 'add', 'subtract', 'vdot', 'ONE', 'ZERO', 'outer')

ONE = Fraction(1, 1)
ZERO = Fraction(0, 1)

# These need no overrides
multiply = alg.multiply
divide = alg.divide
add = alg.add
subtract = alg.subtract
outer = alg.outer


def ones(array_shape):
    """Create and fill a shape with ones."""

    return alg.full(array_shape, ONE)


def vdot(a, b):
    """Dot two vectors."""

    s = ZERO
    for x, y in alg.zipl(a, b):
        s += x * y
    return s


def dot(
    a,
    b,
    *,
    dims=None
):
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
        shape_a = alg.shape(a)
        shape_b = alg.shape(b)
        dims_a = len(shape_a)
        dims_b = len(shape_b)

        # Handle matrices of N-D and M-D size
        if dims_a and dims_b and dims_a > 2 or dims_b > 2:
            if dims_a == 1:
                # Dot product of vector and a M-D matrix
                cols1 = list(alg._extract_dims(b, dims_b, dims_b - 2))
                shape_c = shape_b[:-2] + shape_b[-1:]
                return alg.reshape([[vdot(a, c) for c in col] for col in cols1], shape_c)
            else:
                # Dot product of N-D and M-D matrices
                # Resultant size: `dot(xy, yz) = xz` or `dot(nxy, myz) = nxmz`
                cols2 = (list(alg._extract_dims(b, dims_b, dims_b - 2)) if dims_b > 1 else [[b]])
                rows = list(alg._extract_dims(a, dims_a, dims_a - 1))
                m2 = [[[sum(alg.multiply(row, c)) for c in col] for col in cols2] for row in rows]
                shape_c = shape_a[:-1]
                if dims_b != 1:
                    shape_c += shape_b[:-2] + shape_b[-1:]
                return alg.reshape(m2, shape_c)

    else:
        dims_a, dims_b = dims

    # Optimize to handle arrays <= 2-D
    if dims_a == 1:
        if dims_b == 1:
            # Dot product of two vectors
            return vdot(a, b)
        elif dims_b == 2:
            # Dot product of vector and a matrix
            return [vdot(a, col) for col in alg.zipl(*b)]

    elif dims_a == 2:
        if dims_b == 1:
            # Dot product of matrix and a vector
            return [vdot(row, b) for row in a]
        elif dims_b == 2:
            # Dot product of two matrices
            return [[vdot(row, col) for col in alg.zipl(*b)] for row in a]

    # Trying to dot a number with a vector or a matrix, so just multiply
    return alg.multiply(a, b, dims=(dims_a, dims_b))


def diag(array, k=0):
    """Create a diagonal matrix from a vector or return a vector of the diagonal of a matrix."""

    s = alg.shape(array)
    dims = len(s)
    if not dims or dims > 2:
        raise ValueError('Array must be 1-D or 2-D in shape')

    if dims == 1:
        # Calculate size of matrix to accommodate the diagonal
        size = s[0] - k if k < 0 else (s[0] + k if k else s[0])
        maximum = size - 1
        minimum = 0

        # Create a diagonal matrix with the provided vector
        m = []
        for i in range(size):
            pos = i + k
            idx = i if k >= 0 else pos
            m.append(
                ([ZERO] * alg.clamp(pos, minimum, maximum)) +
                [array[idx] if (0 <= pos < size) else ZERO] +
                ([ZERO] * alg.clamp(size - pos - 1, minimum, maximum))
            )
        return m
    else:
        # Extract the requested diagonal from a rectangular 2-D matrix
        size = s[1]
        d = []
        for i, r in enumerate(array):
            pos = i + k
            if (0 <= pos < size):
                d.append(r[pos])
        return d


def inv(matrix):
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

    Modified to handle greater than 2 x 2 dimensions.
    """

    # Ensure we have a square matrix
    s = alg.shape(matrix)
    dims = len(s)
    if dims < 2 or min(s) != max(s):
        raise ValueError('Matrix must be a N x N matrix')

    # Handle dimensions greater than 2 x 2
    elif dims > 2:
        invert = []
        cols = list(alg._extract_dims(matrix, dims, dims - 2))
        for c in cols:
            invert.append(transpose(inv(c)))
        return alg.reshape(invert, s)

    indices = list(range(s[0]))
    m = alg.acopy(matrix)

    # Create an identity matrix of the same size as our provided vector
    im = diag([ONE] * s[0])

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
        if denom == 0:
            raise ValueError('Matrix is not invertable')

        # We are converting the matrix to the identity and vice versa,
        # So scale the diagonal such that it will now equal 1.
        # Additionally, the same operations will be applied to the identity matrix
        # and will turn it into `m ** -1` (what we are looking for)
        fd_scalar = ONE / denom
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


def transpose(array):
    """
    A simple transpose of a matrix.

    `numpy` offers the ability to specify different axes, but right now,
    we don't have a need for that, nor the desire to figure it out :).
    """

    s = list(reversed(alg.shape(array)))
    total = alg.prod(s)

    # Create the array
    m = []

    # Calculate data sizes
    dims = len(s)
    length = s[-1]

    # Initialize indexes so we can properly write our data
    idx = [0] * dims

    # Traverse the provided array filling our new array
    for i, v in enumerate(alg.flatiter(array), 0):

        # Navigate to the proper index to start writing data.
        # If the dimension hasn't been created yet, create it.
        t = m
        for d, x in enumerate(range(dims - 1)):
            if not t:
                for _ in range(s[d]):
                    t.append([])
            t = t[idx[x]]

        # Initialize the last dimension
        # so we can index at the correct position
        if not t:
            t[:] = [ZERO] * length

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

    return m
