"""HSL class."""
from __future__ import annotations
from .. import hsl as base
from ...css import parse
from ...css import serialize
from ...types import Vector
from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color


class HSL(base.HSL):
    """HSL class."""

    def to_string(
        self,
        parent: Color,
        *,
        alpha: Optional[bool] = None,
        precision: Optional[int] = None,
        fit: str | bool = True,
        none: bool = False,
        color: bool = False,
        comma: bool = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS."""

        return serialize.serialize_css(
            parent,
            func='hsl',
            alpha=alpha,
            precision=precision,
            fit=fit,
            none=none,
            color=color,
            legacy=comma
        )

    def match(
        self,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> Optional[tuple[tuple[Vector, float], int]]:
        """Match a CSS color string."""

        return parse.parse_css(self, string, start, fullmatch)
