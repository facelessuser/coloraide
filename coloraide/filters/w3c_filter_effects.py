"""Provide filters as described by the https://www.w3.org/TR/filter-effects-1/."""
from __future__ import annotations
import math
from ..filters import Filter
from .. import algebra as alg
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def linear_transfer(value: float, slope: float = 1.0, intercept: float = 0.0) -> float:
    """
    Linear transfer function.

    https://drafts.fxtf.org/filter-effects-1/#feFuncRElement
    """

    return value * slope + intercept


class Sepia(Filter):
    """Sepia filter."""

    NAME = 'sepia'
    ALLOWED_SPACES = ('srgb-linear', 'srgb')

    def filter(self, color: Color, amount: float | None, **kwargs: Any) -> None:  # noqa: A003
        """Apply a sepia filter to the color."""

        amount = 1 - alg.clamp(1 if amount is None else amount, 0, 1)

        m = [
            [0.393 + 0.607 * amount, 0.769 - 0.769 * amount, 0.189 - 0.189 * amount],
            [0.349 - 0.349 * amount, 0.686 + 0.314 * amount, 0.168 - 0.168 * amount],
            [0.272 - 0.272 * amount, 0.534 - 0.534 * amount, 0.131 + 0.869 * amount]
        ]

        color[:-1] = alg.dot(m, color[:-1], dims=alg.D2_D1)


class Grayscale(Filter):
    """Grayscale filter."""

    NAME = 'grayscale'
    ALLOWED_SPACES = ('srgb-linear', 'srgb')

    def filter(self, color: Color, amount: float | None, **kwargs: Any) -> None:  # noqa: A003
        """Apply a grayscale filter to the color."""

        amount = 1 - alg.clamp(1 if amount is None else amount, 0, 1)

        m = [
            [0.2126 + 0.7874 * amount, 0.7152 - 0.7152 * amount, 0.0722 - 0.0722 * amount],
            [0.2126 - 0.2126 * amount, 0.7152 + 0.2848 * amount, 0.0722 - 0.0722 * amount],
            [0.2126 - 0.2126 * amount, 0.7152 - 0.7152 * amount, 0.0722 + 0.9278 * amount]
        ]

        color[:-1] = alg.dot(m, color[:-1], dims=alg.D2_D1)


class Saturate(Filter):
    """Saturation filter."""

    NAME = 'saturate'
    ALLOWED_SPACES = ('srgb-linear', 'srgb')

    def filter(self, color: Color, amount: float | None, **kwargs: Any) -> None:  # noqa: A003
        """Apply a saturation filter to the color."""

        amount = alg.clamp(1 if amount is None else amount, 0)

        m = [
            [0.213 + 0.787 * amount, 0.715 - 0.715 * amount, 0.072 - 0.072 * amount],
            [0.213 - 0.213 * amount, 0.715 + 0.285 * amount, 0.072 - 0.072 * amount],
            [0.213 - 0.213 * amount, 0.715 - 0.715 * amount, 0.072 + 0.928 * amount]
        ]

        color[:-1] = alg.dot(m, color[:-1], dims=alg.D2_D1)


class Invert(Filter):
    """Grayscale filter."""

    NAME = 'invert'
    ALLOWED_SPACES = ('srgb-linear', 'srgb')

    def filter(self, color: Color, amount: float | None, **kwargs: Any) -> None:  # noqa: A003
        """Apply an invert filter."""

        amount = alg.clamp(1 if amount is None else amount, 0, 1)
        for e, c in enumerate(color[:-1]):
            color[e] = alg.lerp(amount, 1 - amount, c)


class Opacity(Filter):
    """Opacity filter."""

    NAME = 'opacity'
    ALLOWED_SPACES = ('srgb-linear', 'srgb')

    def filter(self, color: Color, amount: float | None, **kwargs: Any) -> None:  # noqa: A003
        """Apply an opacity filter."""

        amount = alg.clamp(1 if amount is None else amount, 0, 1)
        color[-1] = alg.lerp(0, amount, color[-1])


class Brightness(Filter):
    """Brightness filter."""

    NAME = 'brightness'
    ALLOWED_SPACES = ('srgb-linear', 'srgb')

    def filter(self, color: Color, amount: float | None, **kwargs: Any) -> None:  # noqa: A003
        """Apply a brightness filter."""

        amount = alg.clamp(1 if amount is None else amount, 0)
        for e, c in enumerate(color[:-1]):
            color[e] = linear_transfer(c, amount)


class Contrast(Filter):
    """Contrast filter."""

    NAME = 'contrast'
    ALLOWED_SPACES = ('srgb-linear', 'srgb')

    def filter(self, color: Color, amount: float | None, **kwargs: Any) -> None:  # noqa: A003
        """Apply a contrast filter."""

        amount = alg.clamp(1 if amount is None else amount, 0)
        for e, c in enumerate(color[:-1]):
            color[e] = linear_transfer(c, amount, (1 - amount) * 0.5)


class HueRotate(Filter):
    """Hue rotate filter."""

    NAME = 'hue-rotate'
    ALLOWED_SPACES = ('srgb-linear', 'srgb')

    def filter(self, color: Color, amount: float | None, **kwargs: Any) -> None:  # noqa: A003
        """Apply a hue rotation filter."""

        rad = math.radians(0 if amount is None else amount)
        cos = math.cos(rad)
        sin = math.sin(rad)

        m = [
            [0.213 + cos * 0.787 - sin * 0.213, 0.715 - cos * 0.715 - sin * 0.715, 0.072 - cos * 0.072 + sin * 0.928],
            [0.213 - cos * 0.213 + sin * 0.143, 0.715 + cos * 0.285 + sin * 0.140, 0.072 - cos * 0.072 - sin * 0.283],
            [0.213 - cos * 0.213 - sin * 0.787, 0.715 - cos * 0.715 + sin * 0.715, 0.072 + cos * 0.928 + sin * 0.072]
        ]

        color[:-1] = alg.dot(m, color[:-1], dims=alg.D2_D1)
