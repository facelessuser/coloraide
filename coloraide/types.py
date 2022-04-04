"""Typing."""
from typing import Union, Any, Mapping, Sequence, List, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color

ColorInput = Union['Color', str, Mapping[str, Any]]
VectorLike = Sequence[float]
MatrixLike = Sequence[VectorLike]
ArrayLike = Union[VectorLike, MatrixLike]
Vector = List[float]
Matrix = List[Vector]
Array = Union[Matrix, Vector]
SupportsFloatOrInt = TypeVar('SupportsFloatOrInt', float, int)
