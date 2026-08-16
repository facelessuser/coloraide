# noqa: A005
"""Typing."""
from __future__ import annotations
import sys
from typing import Any, Mapping, Sequence, TypeVar, Union, TypeAlias, TYPE_CHECKING
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

# Vectors, Matrices, and Arrays are assumed to be mutable lists
Vector = list[float]
Matrix = list[Vector]
Tensor = list[Union[Matrix, 'Tensor']]
Array = Matrix | Vector | Tensor

# Anything that resembles a sequence will be considered "like" one of our types above
VectorLike = Sequence[float]
MatrixLike = Sequence[VectorLike]
TensorLike = Sequence[Union[MatrixLike, 'TensorLike']]
ArrayLike = VectorLike | MatrixLike | TensorLike

# Vectors, Matrices, and Arrays of various, specific types
VectorBool = list[bool]
MatrixBool = list[VectorBool]
TensorBool = list[Union[MatrixBool, 'TensorBool']]
ArrayBool = MatrixBool | VectorBool | TensorBool

VectorBoolLike = Sequence[bool]
MatrixBoolLike = Sequence[VectorBoolLike]
TensorBoolLike = Sequence[Union[MatrixBoolLike, 'TensorBoolLike']]
ArrayBoolLike = VectorBoolLike | MatrixBoolLike | TensorBoolLike

VectorInt = list[int]
MatrixInt = list[VectorInt]
TensorInt = list[Union[MatrixInt, 'TensorInt']]
ArrayInt = MatrixInt | VectorInt | TensorInt

VectorIntLike = Sequence[int]
MatrixIntLike = Sequence[VectorIntLike]
TensorIntLike = Sequence[Union[MatrixIntLike, 'TensorIntLike']]
ArrayIntLike = VectorIntLike | MatrixIntLike | TensorIntLike

# General algebra types
EmptyShape = tuple[()]
VectorShape = tuple[int]
MatrixShape = tuple[int, int]
TensorShape = tuple[int, int, int, Unpack[tuple[int, ...]]]

ArrayShape = tuple[int, ...]
Shape = EmptyShape | ArrayShape
ShapeLike = Sequence[int]
DimHints = tuple[int, int]

# For times when we must explicitly say we support `int` and `float`
SupportsFloatOrInt = TypeVar('SupportsFloatOrInt', float, int)


class Plugin:
    """
    Plugin type base class.

    A common class used to help simplify typing in some cases.
    """

    NAME = ""
