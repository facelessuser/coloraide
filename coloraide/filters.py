"""Provide filters as described by the https://www.w3.org/TR/filter-effects-1/."""
from . import algebra as alg
from .interpolate import Lerp
import math
from .types import Vector
from typing import Optional, cast, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color


def linear_transfer(value: float, slope: float = 1.0, intercept: float = 0.0) -> float:
    """
    Linear transfer function.

    https://drafts.fxtf.org/filter-effects-1/#feFuncRElement
    """

    return value * slope + intercept


def sepia(color: 'Color', amount: Optional[float]) -> None:
    """Apply a sepia filter to the color."""

    amount = 1 - alg.clamp(1 if amount is None else amount, 0, 1)

    m = [
        [0.393 + 0.607 * amount, 0.769 - 0.769 * amount, 0.189 - 0.189 * amount],
        [0.349 - 0.349 * amount, 0.686 + 0.314 * amount, 0.168 - 0.168 * amount],
        [0.272 - 0.272 * amount, 0.534 - 0.534 * amount, 0.131 + 0.869 * amount]
    ]

    color._space._coords = cast(Vector, alg.dot(m, color.coords(), dims=alg.D2_D1))


def grayscale(color: 'Color', amount: Optional[float]) -> None:
    """Apply a sepia filter to the color."""

    amount = 1 - alg.clamp(1 if amount is None else amount, 0, 1)

    m = [
        [0.2126 + 0.7874 * amount, 0.7152 - 0.7152 * amount, 0.0722 - 0.0722 * amount],
        [0.2126 - 0.2126 * amount, 0.7152 + 0.2848 * amount, 0.0722 - 0.0722 * amount],
        [0.2126 - 0.2126 * amount, 0.7152 - 0.7152 * amount, 0.0722 + 0.9278 * amount]
    ]

    color._space._coords = cast(Vector, alg.dot(m, color.coords(), dims=alg.D2_D1))


def saturate(color: 'Color', amount: Optional[float]) -> None:
    """Apply a sepia filter to the color."""

    amount = 1 - alg.clamp(1 if amount is None else amount, 0)

    m = [
        [0.213 + 0.787 * amount, 0.715 - 0.715 * amount, 0.072 - 0.072 * amount],
        [0.213 - 0.213 * amount, 0.715 + 0.285 * amount, 0.072 - 0.072 * amount],
        [0.213 - 0.213 * amount, 0.715 - 0.715 * amount, 0.072 + 0.928 * amount]
    ]

    color._space._coords = cast(Vector, alg.dot(m, color.coords(), dims=alg.D2_D1))


def invert(color: 'Color', amount: Optional[float]) -> None:
    """Invert."""

    amount = alg.clamp(1 if amount is None else amount, 0, 1)
    lerp = Lerp(None)
    coords = []
    for c in color.coords():
        coords.append(lerp(amount, 1 - amount, c))
    color._space._coords = coords


def opacity(color: 'Color', amount: Optional[float]) -> None:
    """Invert."""

    amount = alg.clamp(1 if amount is None else amount, 0, 1)
    lerp = Lerp(None)
    color.alpha = lerp(0, amount, color.alpha)


def brightness(color: 'Color', amount: Optional[float]) -> None:
    """Brightness."""

    amount = alg.clamp(1 if amount is None else amount, 0)
    coords = []
    for c in color.coords():
        coords.append(linear_transfer(c, amount))
    color._space._coords = coords


def contrast(color: 'Color', amount: Optional[float]) -> None:
    """Contrast."""

    amount = alg.clamp(1 if amount is None else amount, 0)
    coords = []
    for c in color.coords():
        coords.append(linear_transfer(c, amount, (1 - amount) * 0.5))
    color._space._coords = coords


def hue_rotate(color: 'Color', amount: Optional[float]) -> None:
    """Hue rotate."""

    rad = math.radians(0 if amount is None else amount)
    cos = math.cos(rad)
    sin = math.sin(rad)

    m = [
        [0.213 + cos * 0.787 - sin * 0.213, 0.715 - cos * 0.715 - sin * 0.715, 0.072 - cos * 0.072 + sin * 0.928],
        [0.213 - cos * 0.213 + sin * 0.143, 0.715 + cos * 0.285 + sin * 0.140, 0.072 - cos * 0.072 - sin * 0.283],
        [0.213 - cos * 0.213 - sin * 0.787, 0.715 - cos * 0.715 + sin * 0.715, 0.072 + cos * 0.928 + sin * 0.072]
    ]

    color._space._coords = cast(Vector, alg.dot(m, color.coords(), dims=alg.D2_D1))


SUPPORTED = {
    'sepia': sepia,
    'grayscale': grayscale,
    'saturate': saturate,
    'invert': invert,
    'brightness': brightness,
    'contrast': contrast,
    'hue-rotate': hue_rotate,
    'opacity': opacity
}


def filters(color: 'Color', name: str, amount: Optional[float] = None) -> None:
    """Filter."""

    try:
        return SUPPORTED[name](color, amount)
    except KeyError:
        raise ValueError("'{}' filter is not supported".format(name))
