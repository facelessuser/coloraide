# noqa: A005
"""Typing."""
from __future__ import annotations
import sys
from typing import Any, Mapping, Sequence, TypeVar, Union, TYPE_CHECKING
if (3, 11) <= sys.version_info:
    from typing import Unpack
else:
    from typing_extensions import Unpack
if TYPE_CHECKING:  # pragma: no cover
    from .color import Color

# Generic color template for handling inherited colors
AnyColor = TypeVar('AnyColor', bound='Color')

# Color inputs which can be an object, string, or a mapping describing the color.
ColorInput = Union['Color', str, Mapping[str, Any]]

# Generic Vectors, Matrices, and Arrays are assumed to be mutable lists
Number = TypeVar('Number', bool, int, float)
StrictNumber= TypeVar('StrictNumber', int, float)
VectorT = list[Number]
MatrixT = list[VectorT[Number]]
TensorT = list[Union[MatrixT[Number], 'TensorT[Number]']]
ArrayT = VectorT[Number] | MatrixT[Number] | TensorT[Number]

# Anything that resembles a sequence will be considered "like" one of our generic types above
VectorTLike = Sequence[Number]
MatrixTLike = Sequence[VectorTLike[Number]]
TensorTLike = Sequence[Union[MatrixTLike[Number], 'TensorTLike[Number]']]
ArrayTLike = VectorTLike[Number] | MatrixTLike[Number] | TensorTLike[Number]

# Float Vectors, Matrices, and Arrays are assumed to be mutable lists
Vector = VectorT[float]
Matrix = MatrixT[float]
Tensor = TensorT[float]
Array = ArrayT[float]

# Anything that resembles a sequence will be considered "like" one of our float types above
VectorLike = VectorTLike[float]
MatrixLike = MatrixTLike[float]
TensorLike = TensorTLike[float]
ArrayLike = ArrayTLike[float]

# Boolean Vectors, Matrices, and Arrays are assumed to be mutable lists
VectorBool = VectorT[bool]
MatrixBool = MatrixT[bool]
TensorBool = TensorT[bool]
ArrayBool = ArrayT[bool]

# Anything that resembles a sequence will be considered "like" one of our boolean types above
VectorBoolLike = VectorTLike[bool]
MatrixBoolLike = MatrixTLike[bool]
TensorBoolLike = TensorTLike[bool]
ArrayBoolLike = ArrayTLike[bool]

# Integer Vectors, Matrices, and Arrays are assumed to be mutable lists
VectorInt = VectorT[int]
MatrixInt = MatrixT[int]
TensorInt = TensorT[int]
ArrayInt = ArrayT[int]

# Anything that resembles a sequence will be considered "like" one of our integer types above
VectorIntLike = VectorTLike[int]
MatrixIntLike = MatrixTLike[int]
TensorIntLike = TensorTLike[int]
ArrayIntLike = ArrayTLike[int]

# General algebra types
EmptyShape = tuple[()]
VectorShape = tuple[int]
MatrixShape = tuple[int, int]
TensorShape = tuple[int, int, int, Unpack[tuple[int, ...]]]

ArrayShape = tuple[int, ...]
Shape = EmptyShape | ArrayShape
ShapeLike = Sequence[int]
DimHints = tuple[int, int]


class Plugin:
    """
    Plugin type base class.

    A common class used to help simplify typing in some cases.
    """

    NAME = ""
