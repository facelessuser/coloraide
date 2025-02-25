# noqa: A005
"""Typing."""
from __future__ import annotations
from typing import Union, Any, Mapping, Sequence, TypeVar, TypeAlias, TYPE_CHECKING

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
TensorShape: TypeAlias = "tuple[int, int, int, *tuple[int, ...]]"

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
