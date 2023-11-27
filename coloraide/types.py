"""Typing."""
from __future__ import annotations
from typing import Union, Any, Mapping, Sequence, List, Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color

ColorInput = Union['Color', str, Mapping[str, Any]]

# Vectors, Matrices, and Arrays are assumed to be mutable lists
Vector = List[float]
Matrix = List[Vector]
Tensor = List[List[List[Union[float, Any]]]]
Array = Union[Matrix, Vector, Tensor]

# Anything that resembles a sequence will be considered "like" one of our types above
VectorLike = Sequence[float]
MatrixLike = Sequence[VectorLike]
TensorLike = Sequence[Sequence[Sequence[Union[float, Any]]]]
ArrayLike = Union[VectorLike, MatrixLike, TensorLike]

# Vectors, Matrices, and Arrays of various, specific types
VectorBool = List[bool]
MatrixBool = List[VectorBool]
TensorBool = List[List[List[Union[bool, Any]]]]
ArrayBool = Union[MatrixBool, VectorBool, TensorBool]

VectorInt = List[int]
MatrixInt = List[VectorInt]
TensorInt = List[List[List[Union[int, Any]]]]
ArrayInt = Union[MatrixInt, VectorInt, TensorInt]

# General algebra types
Shape = Tuple[int, ...]
ShapeLike = Sequence[int]
DimHints = Tuple[int, int]

# For times when we must explicitly say we support `int` and `float`
SupportsFloatOrInt = TypeVar('SupportsFloatOrInt', float, int)

MathType = TypeVar('MathType', float, VectorLike, MatrixLike, TensorLike)


class Plugin:
    """
    Plugin type base class.

    A common class used to help simplify typing in some cases.
    """

    NAME = ""
