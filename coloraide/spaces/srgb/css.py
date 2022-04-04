"""SRGB color class."""
from .. import srgb as base
from ...css import parse
from ...css import serialize
from typing import Optional, Union, Any, Tuple, TYPE_CHECKING
from ...types import Vector

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color


class SRGB(base.SRGB):
    """SRGB class."""

    def to_string(
        self,
        parent: 'Color',
        *,
        alpha: Optional[bool] = None,
        precision: Optional[int] = None,
        fit: Union[bool, str] = True,
        none: bool = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS."""

        return serialize.serialize_css(
            parent,
            func='rgb',
            alpha=alpha,
            precision=precision,
            fit=fit,
            none=none,
            color=kwargs.get('color', False),
            hexa=kwargs.get('hex', False),
            name=kwargs.get('names', False),
            legacy=kwargs.get('comma', False),
            upper=kwargs.get('upper', False),
            percent=kwargs.get('percent', False),
            compress=kwargs.get('compress', False),
            scale=255
        )

    @classmethod
    def match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> Optional[Tuple[Tuple[Vector, float], int]]:
        """Match a CSS color string."""

        return parse.parse_css(cls, string, start, fullmatch)
