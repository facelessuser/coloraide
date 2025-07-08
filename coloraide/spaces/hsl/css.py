"""HSL class."""
from __future__ import annotations
from .. import hsl as base
from ...css import parse
from ...css import serialize
from ...types import Vector
from typing import Any, Sequence, TYPE_CHECKING

if TYPE_CHECKING:  #pragma: no cover
    from ...color import Color


class HSL(base.HSL):
    """HSL class."""

    def to_string(
        self,
        parent: Color,
        *,
        alpha: bool | None = None,
        precision: int | Sequence[int] | None = None,
        rounding: str | None = None,
        fit: bool | str | dict[str, Any] = True,
        none: bool = False,
        color: bool = False,
        percent: bool | Sequence[bool] = False,
        comma: bool = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS."""

        if comma:
            if isinstance(percent, bool):
                percent = True
            else:
                percent = [False, True, True, *percent[3:4]]

        return serialize.serialize_css(
            parent,
            func='hsl',
            alpha=alpha,
            precision=precision,
            rounding=rounding,
            fit=fit,
            none=none,
            color=color,
            legacy=comma,
            percent=percent,
            scale=100
        )

    def match(
        self,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> tuple[tuple[Vector, float], int] | None:
        """Match a CSS color string."""

        return parse.parse_css(self, string, start, fullmatch)
