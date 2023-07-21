"""Typing."""
from __future__ import annotations
from typing import Union, Any, Mapping, Sequence, List, Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color

ColorInput = Union['Color', str, Mapping[str, Any]]

# Vectors, Matrices, and Arrays are assumed to be mutable lists
Vector = List[float]
Matrix = List[Vector]
Array = Union[Matrix, Vector]

# Anything that resembles a sequence will be considered "like" one of our types above
VectorLike = Sequence[float]
MatrixLike = Sequence[VectorLike]
ArrayLike = Union[VectorLike, MatrixLike]

# General algebra types
Shape = Tuple[int, ...]
ShapeLike = Sequence[int]
DimHints = Tuple[int, int]

# For times when we must explicitly say we support `int` and `float`
SupportsFloatOrInt = TypeVar('SupportsFloatOrInt', float, int)


class Plugin:
    """
    Plugin type base class.

    A common class used to help simplify typing in some cases.
    """

    NAME = ""
