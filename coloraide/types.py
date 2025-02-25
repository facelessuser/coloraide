# noqa: A005
"""Typing."""
from __future__ import annotations
import sys
from typing import Union, Any, Mapping, Sequence, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color

ColorInput = Union['Color', str, Mapping[str, Any]]

# Vectors, Matrices, and Arrays are assumed to be mutable lists
Vector = list[float]
Matrix = list[Vector]
Tensor = list[list[list[float | Any]]]
Array = Matrix | Vector | Tensor

# Anything that resembles a sequence will be considered "like" one of our types above
VectorLike = Sequence[float]
MatrixLike = Sequence[VectorLike]
TensorLike = Sequence[Sequence[Sequence[float | Any]]]
ArrayLike = VectorLike | MatrixLike | TensorLike

# Vectors, Matrices, and Arrays of various, specific types
VectorBool = list[bool]
MatrixBool = list[VectorBool]
TensorBool = list[list[list[bool | Any]]]
ArrayBool = MatrixBool | VectorBool | TensorBool

VectorInt = list[int]
MatrixInt = list[VectorInt]
TensorInt = list[list[list[int | Any]]]
ArrayInt = MatrixInt | VectorInt | TensorInt

# General algebra types
FloatShape = tuple[()]
VectorShape = tuple[int]
MatrixShape = tuple[int, int]

if (3, 11) <= sys.version_info:
    TensorShape = tuple[int, int, int, *tuple[int, ...]]
else:
    # For versions below 3.10, just treat tensors as one deper than a Matrix.
    # We don't directly use tensors in ColorAide even though they are supported.
    TensorShape = tuple[int, int, int]

ArrayShape = tuple[int, ...]
Shape = FloatShape | ArrayShape
ShapeLike = Sequence[int]
DimHints = tuple[int, int]

# For times when we must explicitly say we support `int` and `float`
SupportsFloatOrInt = TypeVar('SupportsFloatOrInt', float, int)

ArrayType = TypeVar('ArrayType', float, VectorLike, MatrixLike, TensorLike)


class Plugin:
    """
    Plugin type base class.

    A common class used to help simplify typing in some cases.
    """

    NAME = ""
