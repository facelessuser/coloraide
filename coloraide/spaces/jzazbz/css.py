"""Jzazbz class."""
from __future__ import annotations
from .. import jzazbz as base
from ...css import parse
from ...css import serialize
from ...types import Vector, TypeColor
from typing import Any, Sequence


class Jzazbz(base.Jzazbz):
    """Jzazbz class."""

    def to_string(
        self,
        parent: TypeColor,
        *,
        alpha: bool | None = None,
        precision: int | Sequence[int] | None = None,
        fit: bool | str | dict[str, Any] = True,
        none: bool = False,
        color: bool = False,
        percent: bool | Sequence[bool] = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS."""

        return serialize.serialize_css(
            parent,
            func='jzazbz',
            alpha=alpha,
            precision=precision,
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
