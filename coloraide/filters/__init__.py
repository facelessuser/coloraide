"""Provides a plugin system for filtering colors."""
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from ..types import Plugin
from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class Filter(Plugin, metaclass=ABCMeta):
    """Filter a color."""

    NAME = ''
    DEFAULT_SPACE = 'srgb-linear'
    ALLOWED_SPACES = ('srgb-linear',)  # type: tuple[str, ...]

    @abstractmethod
    def filter(self, color: Color, amount: Optional[float], **kwargs: Any) -> None:  # noqa: A003
        """Filter the given color."""


def filters(
    color: Color,
    name: str,
    amount: Optional[float] = None,
    space: Optional[str] = None,
    in_place: bool = False,
    **kwargs: Any
) -> Color:
    """Filter."""

    f = color.FILTER_MAP.get(name)
    if not f:
        raise ValueError("'{}' filter is not supported".format(name))

    if space is None:
        space = f.DEFAULT_SPACE

    if space not in f.ALLOWED_SPACES:
        raise ValueError(
            "The '{}' only supports filtering in the {} spaces, not '{}'".format(name, str(f.ALLOWED_SPACES), space)
        )

    current = color.space()
    c = color.convert(space, in_place=in_place)
    f.filter(c, amount, **kwargs)
    return c.convert(current, in_place=True)
