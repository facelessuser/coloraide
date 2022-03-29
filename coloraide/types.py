"""Typing."""
from typing import Union, Any, Mapping, Sequence, List, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color

ColorInput = Union['Color', str, Mapping[str, Any]]
Vector = Sequence[float]
Matrix = Sequence[Sequence[float]]
Array = Union[Vector, Matrix]
MutableVector = List[float]
MutableMatrix = List[List[float]]
MutableArray = Union[MutableMatrix, MutableVector]
SupportsFloatOrInt = TypeVar('SupportsFloatOrInt', float, int)
