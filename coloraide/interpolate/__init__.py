"""
Interpolation methods.

Originally, the base code for `interpolate`, `mix` and `steps` was ported from the
https://colorjs.io project. Since that time, there has been significant modifications
that add additional features etc. The base logic though is attributed to the original
authors.

In general, the logic mimics in many ways the `color-mix` function as outlined in the Level 5
color draft (Oct 2020), but the initial approach was modeled directly off of the work done in
color.js.
---
Original Authors: Lea Verou, Chris Lilley
License: MIT (As noted in https://github.com/LeaVerou/color.js/blob/master/package.json)
"""
from .bezier import color_bezier_lerp
from .piecewise import color_piecewise_lerp
from .common import Interpolator, hint, stop  # noqa: F401
from typing import Callable, Dict

__all__ = ('stop', 'hint', 'get_interpolator')


SUPPORTED = {
    "linear": color_piecewise_lerp,
    "bezier": color_bezier_lerp
}  # type: Dict[str, Callable[..., Interpolator]]


def get_interpolator(interpolator: str) -> Callable[..., Interpolator]:
    """Get desired blend mode."""

    try:
        return SUPPORTED[interpolator]
    except KeyError:
        raise ValueError("'{}' is not a recognized interpolator".format(interpolator))
