"""Utilities."""
from __future__ import annotations
import math
from functools import wraps
from . import algebra as alg
from .types import Vector, VectorLike
from typing import Any, Callable, Sequence

DEF_PREC = 5
DEF_ROUND_MODE = 'digits'
DEF_FIT_TOLERANCE = 0.000075
DEF_ALPHA = 1.0
DEF_MIX = 0.5
DEF_HUE_ADJ = "shorter"
DEF_INTERPOLATE = "oklab"
DEF_FIT = "lch-chroma"
DEF_HARMONY = "oklch"
DEF_DELTA_E = "76"
DEF_AVERAGE = 'srgb-linear'
DEF_CHROMATIC_ADAPTATION = "bradford"
DEF_CONTRAST = "wcag21"
DEF_CCT = "robertson-1968"
DEF_INTERPOLATOR = "linear"

ACHROMATIC_THRESHOLD = 1e-4
ACHROMATIC_THRESHOLD_SM = 1e-6

# PQ Constants
# https://en.wikipedia.org/wiki/High-dynamic-range_video#Perceptual_quantizer
M1 = 2610 / 16384
M2 = 2523 / 32
C1 = 3424 / 4096
C2 = 2413 / 128
C3 = 2392 / 128


def xy_to_xyz(xy: VectorLike, Y: float = 1.0, scale: float = 1.0) -> Vector:
    """
    Convert `xyY` to `xyz`.

    In many cases, we are dealing with chromaticity values with no Y value,
    in this case, assume 1 unless otherwise specified. Generally, scale is
    also assumed to be between 0 - 1, but allow changing scale if we are
    dealing with things like 0 - 100, etc.
    """

    x, y = xy
    return [0.0, 0.0, 0.0] if y == 0 else [(x * Y) / y, Y, (scale - x - y) * Y / y]


def xyz_to_xyY(xyz: VectorLike, white: VectorLike = (0.0, 0.0)) -> Vector:
    """
    XYZ to `xyY`.

    If a white point chromaticity pair is given, black will be aligned with the achromatic axis.
    """

    x, y, z = xyz
    d = x + y + z
    return [white[0], white[1], y] if d == 0 else [x / d, y / d, y]


def xy_to_uv(xy: VectorLike) -> Vector:
    """XYZ to UV."""

    u, v = xy_to_uv_1960(xy)
    return [u, v * (3 / 2)]


def uv_to_xy(uv: VectorLike) -> Vector:
    """XYZ to UV."""

    return uv_1960_to_xy([uv[0], uv[1] * (2 / 3)])


def xy_to_uv_1960(xy: VectorLike) -> Vector:
    """XYZ to UV."""

    x, y = xy
    denom = (12 * y - 2 * x + 3)
    return [0.0, 0.0] if denom == 0 else [(4 * x) / denom, (6 * y) / denom]


def uv_1960_to_xy(uv: VectorLike) -> Vector:
    """XYZ to UV."""

    u, v = uv
    denom = (2 * u - 8 * v + 4)
    return [0.0, 0.0] if denom == 0 else [(3 * u) / denom, (2 * v) / denom]


def pq_st2084_oetf(
    values: VectorLike,
    c1: float = C1,
    c2: float = C2,
    c3: float = C3,
    m1: float = M1,
    m2: float = M2
) -> Vector:
    """Perceptual quantizer (SMPTE ST 2084) - OETF."""

    adjusted = []
    for c in values:
        c = alg.spow(c / 10000, m1)
        adjusted.append(alg.spow((c1 + c2 * c) / (1 + c3 * c), m2))
    return adjusted


def pq_st2084_eotf(
    values: VectorLike,
    c1: float = C1,
    c2: float = C2,
    c3: float = C3,
    m1: float = M1,
    m2: float = M2
) -> Vector:
    """Perceptual quantizer (SMPTE ST 2084) - EOTF."""

    im1 = 1 / m1
    im2 = 1 / m2

    adjusted = []
    for c in values:
        c = alg.spow(c, im2)
        adjusted.append(10000 * alg.spow(max((c - c1), 0) / (c2 - c3 * c), im1))
    return adjusted


def rgb_scale(vec: VectorLike) -> Vector:
    """
    Scale the RGB vector.

    If minimum is less than zero, behaves like min/max normalization.
    If minimum is not less than zero, behaves like maximum normalization.
    """

    # `(v - min_v)`
    w = min(vec)
    if w < 0.0:
        vec = [v - w for v in vec]

    # `(max_v - min_v)`
    m = max(vec)

    # `(v - min_v) / (max_v - min_v)`
    return [v / m if m else v for v in vec]


def scale100(coords: Vector) -> Vector:
    """Scale from 1 to 100."""

    return [c * 100 for c in coords]


def scale1(coords: Vector) -> Vector:
    """Scale from 1 to 100."""

    return [c * 0.01 for c in coords]


def xyz_to_absxyz(xyzd65: VectorLike, yw: float = 100) -> Vector:
    """XYZ to Absolute XYZ."""

    return [c * yw for c in xyzd65]


def absxyz_to_xyz(absxyzd65: VectorLike, yw: float = 100) -> Vector:
    """Absolute XYZ to XYZ."""

    return [c / yw for c in absxyzd65]


def constrain_hue(hue: float) -> float:
    """Constrain hue to [0, 360)."""

    return hue % 360 if not math.isnan(hue) else hue


def get_index(obj: Sequence[Any], idx: int, default: Any = None) -> Any:
    """Get sequence value at index or return default if not present."""

    try:
        return obj[idx]
    except IndexError:
        return default


def cmp_coords(c1: VectorLike, c2: VectorLike) -> bool:
    """Compare coordinates."""

    if len(c1) != len(c2):
        return False
    else:
        return all(map(lambda a, b: (math.isnan(a) and math.isnan(b)) or a == b, c1, c2))


def fmt_float(f: float, p: int = 0, rounding: str = 'digits', percent: float = 0.0, offset: float = 0.0) -> str:
    """
    Set float precision and trim precision zeros.

    -   `p`: Rounding precision.

    -   `rounding`: Specify specific rounding mode.

    -   `percent`: Treat as a percent.

    -   `offset`: Apply an offset (used in conjunction with `percent`).

    """

    # Undefined values should be none
    if math.isnan(f):
        return "none"

    # Infinite values do not get rounded
    if not math.isfinite(f):
        raise ValueError(f'Cannot format non-finite number {f}')

    # Apply rounding
    f = (f + offset) / (percent * 0.01) if percent else f
    start, p = alg._round_location(f, p, rounding)
    value = alg.round_half_up(f, p)

    # Format the string.
    if (p - start + 1) > 17:
        # If we are outputting numbers beyond 17 digits, just use normal output.
        s = str(value).removesuffix('.0')
    else:
        # Avoid scientific notation for numbers with 17 digits (double-precision number of decimals).
        s = f"{{:0.{1 if p < 1 else p}f}}".format(value).rstrip('0').rstrip('.')
    return s + '%' if percent else s


def debug(func:  Callable[..., Any]) -> Callable[..., Any]:  # pragma: no cover
    """Intercept function call and print arguments and results."""

    @wraps(func)
    def _wrapper(*args: Any, **kwargs: Any) -> Any:
        """Print debug information about the function."""

        print(f"<debug> Calling '{func.__name__}' with args={args} and kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"<debug> '{func.__name__}' returned {result}")
        return result

    return _wrapper
