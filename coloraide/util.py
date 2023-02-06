"""Utilities."""
from __future__ import annotations
import math
import warnings
from functools import wraps
from . import algebra as alg
from .types import Vector, VectorLike
from typing import Any, Callable

DEF_PREC = 5
DEF_FIT_TOLERANCE = 0.000075
DEF_ALPHA = 1.0
DEF_MIX = 0.5
DEF_HUE_ADJ = "shorter"
DEF_INTERPOLATE = "oklab"
DEF_FIT = "lch-chroma"
DEF_HARMONY = "oklch"
DEF_DELTA_E = "76"

# Maximum luminance in PQ is 10,000 cd/m^2
# Relative XYZ has Y=1 for media white
# BT.2048 says media white Y=203 at PQ 58
#
# This is confirmed here: https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BT.2408-3-2019-PDF-E.pdf
YW = 203

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
    return [0, 0, 0] if y == 0 else [(x * Y) / y, Y, (scale - x - y) * Y / y]


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
    if denom != 0:
        u = (4 * x) / denom
        v = (6 * y) / denom
    else:
        u = v = 0

    return [u, v]


def uv_1960_to_xy(uv: VectorLike) -> Vector:
    """XYZ to UV."""

    u, v = uv
    denom = (2 * u - 8 * v + 4)
    if denom != 0:
        x = (3 * u) / denom
        y = (2 * v) / denom
    else:
        x = y = 0

    return [x, y]


def xyz_to_xyY(xyz: VectorLike, white: VectorLike) -> Vector:
    """XYZ to `xyY`."""

    x, y, z = xyz
    d = x + y + z
    return [white[0], white[1], y] if d == 0 else [x / d, y / d, y]


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
        c = alg.npow(c / 10000, m1)
        r = (c1 + c2 * c) / (1 + c3 * c)
        adjusted.append(alg.npow(r, m2))
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
        c = alg.npow(c, im2)
        r = (c - c1) / (c2 - c3 * c)
        adjusted.append(10000 * alg.npow(r, im1))
    return adjusted


def xyz_d65_to_absxyzd65(xyzd65: VectorLike, yw: float = YW) -> Vector:
    """XYZ D65 to Absolute XYZ D65."""

    return [max(c * yw, 0) for c in xyzd65]


def absxyzd65_to_xyz_d65(absxyzd65: VectorLike, yw: float = YW) -> Vector:
    """Absolute XYZ D65 XYZ D65."""

    return [max(c / yw, 0) for c in absxyzd65]


def constrain_hue(hue: float) -> float:
    """Constrain hue to [0, 360)."""

    return hue % 360 if not alg.is_nan(hue) else hue


def cmp_coords(c1: VectorLike, c2: VectorLike) -> bool:
    """Compare coordinates."""

    if len(c1) != len(c2):
        return False
    else:
        return all(map(lambda a, b: (math.isnan(a) and math.isnan(b)) or a == b, c1, c2))


def fmt_float(f: float, p: int = 0, percent: float = 0.0, offset: float = 0.0) -> str:
    """
    Set float precision and trim precision zeros.

    0: Round to whole integer
    -1: Full precision
    <positive number>: precision level
    """

    if alg.is_nan(f):
        return "none"

    value = alg.round_to((f + offset) / (percent * 0.01) if percent else f, p)
    string = ('{{:{}f}}'.format('.53' if p == -1 else '.' + str(p))).format(value)
    s = string if value.is_integer() and p == 0 else string.rstrip('0').rstrip('.')
    return '{}%'.format(s) if percent else s


def deprecated(message: str, stacklevel: int = 2) -> Callable[..., Any]:  # pragma: no cover
    """
    Raise a `DeprecationWarning` when wrapped function/method is called.

    Usage:

        @deprecated("This method will be removed in version X; use Y instead.")
        def some_method()"
            pass
    """

    def _wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def _deprecated_func(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                "'{}' is deprecated. {}".format(func.__name__, message),
                category=DeprecationWarning,
                stacklevel=stacklevel
            )
            return func(*args, **kwargs)
        return _deprecated_func
    return _wrapper


def warn_deprecated(message: str, stacklevel: int = 2) -> None:  # pragma: no cover
    """Warn deprecated."""

    warnings.warn(
        message,
        category=DeprecationWarning,
        stacklevel=stacklevel
    )
