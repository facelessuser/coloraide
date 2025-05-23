"""Contrast."""
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from ..types import Plugin, AnyColor
from typing import Any


class ColorContrast(Plugin, metaclass=ABCMeta):
    """Color contrast plugin class."""

    NAME = ''

    @abstractmethod
    def contrast(self, color1: AnyColor, color2: AnyColor, **kwargs: Any) -> float:
        """Get the contrast of the two provided colors."""


def contrast(name: str | None, color1: AnyColor, color2: AnyColor, **kwargs: Any) -> float:
    """Get the appropriate contrast plugin."""

    if name is None:
        name = color1.CONTRAST

    method = color1.CONTRAST_MAP.get(name)
    if not method:
        raise ValueError(f"'{name}' contrast method is not supported")

    return method.contrast(color1, color2, **kwargs)
