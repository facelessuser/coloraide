"""HWB class."""
from __future__ import annotations
from .. import hwb as base
from ...css import parse
from ...css import serialize
from ...types import Vector
from typing import Any, TYPE_CHECKING, Sequence

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color


class HWB(base.HWB):
    """HWB class."""

    def to_string(
        self,
        parent: Color,
        *,
        alpha: bool | None = None,
        precision: int | None = None,
        fit: bool | str | dict[str, Any] = True,
        none: bool = False,
        color: bool = False,
        percent: bool | Sequence[bool] | None = None,
        **kwargs: Any
    ) -> str:
        """Convert to CSS."""

        if percent is None:
            percent = False if color else True

        return serialize.serialize_css(
            parent,
            func='hwb',
            alpha=alpha,
            precision=precision,
            fit=fit,
            none=none,
            color=color,
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
