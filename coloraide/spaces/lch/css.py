"""LCh class."""
from __future__ import annotations
from .. import lch as base
from ...css import parse
from ...css import serialize
from ...types import Vector
from typing import Any, TYPE_CHECKING, Sequence

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color


class LCh(base.CIELCh):
    """LCh class."""

    def to_string(
        self,
        parent: Color,
        *,
        alpha: bool | None = None,
        precision: int | None = None,
        precision_alpha: int | None = None,
        fit: bool | str | dict[str, Any] = True,
        none: bool = False,
        color: bool = False,
        percent: bool | Sequence[bool] = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS."""

        return serialize.serialize_css(
            parent,
            func='lch',
            alpha=alpha,
            precision=precision,
            precision_alpha=precision_alpha,
            fit=fit,
            none=none,
            color=color,
            percent=percent
        )

    def match(
        self,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> tuple[tuple[Vector, float], int] | None:
        """Match a CSS color string."""

        return parse.parse_css(self, string, start, fullmatch)
