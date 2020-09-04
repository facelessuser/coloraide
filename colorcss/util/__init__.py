"""Utilities."""
import decimal
import math
import re

__all__ = ("clamp", "fmt_float", "round_half_up")

RE_FLOAT_TRIM = re.compile(r'^(?P<keep>\d+)(?P<trash>\.0+|(?P<keep2>\.\d*[1-9])0+)$')
INF = float('inf')


def clamp(value, mn=None, mx=None):
    """Clamp the value to the the given minimum and maximum."""

    if mn is None and mx is None:
        return value
    elif mn is None:
        return min(value, mx)
    elif mx is None:
        return max(value, mn)
    else:
        return max(min(value, mx), mn)


def fmt_float(f, p=0):
    """Set float precision and trim precision zeros."""

    if p == INF:
        string = str(decimal.Decimal(f))
    else:
        string = str(
            decimal.Decimal(f).quantize(decimal.Decimal('0.' + ('0' * p) if p > 0 else '0'), decimal.ROUND_HALF_UP)
        )

    m = RE_FLOAT_TRIM.match(string)
    if m:
        string = m.group('keep')
        if m.group('keep2'):
            string += m.group('keep2')
    return string


def round_half_up(n, scale=0):
    """Round half up."""

    if scale == INF:
        return n
    mult = 10 ** scale
    return math.floor(n * mult + 0.5) / mult
