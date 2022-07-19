"""Contrast."""
from abc import ABCMeta, abstractmethod
from ..types import Plugin
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class ColorContrast(Plugin, metaclass=ABCMeta):
    """Color contrast plugin class."""

    NAME = ''

    @abstractmethod
    def contrast(self, color1: 'Color', color2: 'Color', **kwargs: Any) -> float:
        """Get the contrast of the two provided colors."""


def contrast(name: Optional[str], color1: 'Color', color2: 'Color', **kwargs: Any) -> float:
    """Get the appropriate contrast plugin."""

    if name is None:
        name = color1.CONTRAST

    try:
        func = color1.CONTRAST_MAP[name].contrast
    except KeyError:
        raise ValueError("'{}' contrast method is not supported".format(name))

    return func(color1, color2, **kwargs)
