# noqa: A005
"""Typing."""
from __future__ import annotations
import sys
from typing import Union, Any, Mapping, Sequence, List, Tuple, TypeVar, TYPE_CHECKING
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
Vector = List[float]
Matrix = List[Vector]
Tensor = List[Union[Matrix, 'Tensor']]
Array = Union[Matrix, Vector, Tensor]

# Anything that resembles a sequence will be considered "like" one of our types above
VectorLike = Sequence[float]
MatrixLike = Sequence[VectorLike]
TensorLike = Sequence[Union[MatrixLike, 'TensorLike']]
ArrayLike = Union[VectorLike, MatrixLike, TensorLike]

# Vectors, Matrices, and Arrays of various, specific types
VectorBool = List[bool]
MatrixBool = List[VectorBool]
TensorBool = List[Union[MatrixBool, 'TensorBool']]
ArrayBool = Union[MatrixBool, VectorBool, TensorBool]

VectorInt = List[int]
MatrixInt = List[VectorInt]
TensorInt = List[Union[MatrixInt, 'TensorInt']]
ArrayInt = Union[MatrixInt, VectorInt, TensorInt]

# General algebra types
EmptyShape = Tuple[()]
VectorShape = Tuple[int]
MatrixShape = Tuple[int, int]
TensorShape = Tuple[int, int, int, Unpack[Tuple[int, ...]]]

ArrayShape = Tuple[int, ...]
Shape = Union[EmptyShape, ArrayShape]
ShapeLike = Sequence[int]
DimHints = Tuple[int, int]

# For times when we must explicitly say we support `int` and `float`
SupportsFloatOrInt = TypeVar('SupportsFloatOrInt', float, int)

ArrayType = TypeVar('ArrayType', float, VectorLike, MatrixLike, TensorLike)


class Plugin:
    """
    Plugin type base class.

    A common class used to help simplify typing in some cases.
    """

    NAME = ""
