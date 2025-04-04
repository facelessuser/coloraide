"""Temperature plugin."""
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from ..types import Plugin, Vector, AnyColor
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  #pragma: no cover
    from ..color import Color


class CCT(Plugin, metaclass=ABCMeta):
    """Delta E plugin class."""

    NAME = ''

    @abstractmethod
    def to_cct(self, color: Color, **kwargs: Any) -> Vector:
        """Calculate a color's CCT."""

    @abstractmethod
    def from_cct(
        self,
        color: type[AnyColor],
        space: str,
        kelvin: float,
        duv: float,
        scale: bool,
        scale_space: str | None,
        **kwargs: Any
    ) -> AnyColor:
        """Calculate a color that satisfies the CCT."""


def cct(name: str | None, color: type[AnyColor] | AnyColor) -> CCT:
    """Get the appropriate contrast plugin."""

    if name is None:
        name = color.CCT

    method = color.CCT_MAP.get(name)
    if not method:
        raise ValueError(f"'{name}' CCT method is not supported")

    return method
