"""Utilities."""
import decimal
import math
import re

__all__ = ("clamp", "fmt_float", "NAN", "ZERO_POINT")

RE_FLOAT_TRIM = re.compile(r'^(?P<keep>-?\d+)(?P<trash>\.0+|(?P<keep2>\.\d*[1-9])0+)$')
NAN = float('nan')
INF = float('inf')
ZERO_POINT = 0.0005
DEF_PREC = 5


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


def adjust_precision(f, p):
    """Adjust precision and scale."""

    with decimal.localcontext() as ctx:
        if p > 0:
             # Set precision
            ctx.prec = p
        ctx.rounding = decimal.ROUND_HALF_UP

        if p == -1:
            # Full precision
            value = decimal.Decimal(f)
        elif p == 0:
            # Just round to integer
            value = decimal.Decimal(round_half_up(f))
        else:
            # Round to precision
            value = (decimal.Decimal(f) * decimal.Decimal('1.0'))
            exp = value.as_tuple().exponent
            if exp < 0 and abs(value.as_tuple().exponent) > p:
                value = value.quantize(decimal.Decimal(10) ** -p)

        if value.is_zero():
            value = abs(value)

        return float(value)


def fmt_float(f, p=0):
    """
    Set float precision and trim precision zeros.

    0: Round to whole integer
    -1: Full precision
    <positive number>: precision level
    """

    value = adjust_precision(f, p)
    string = ('{{:{}f}}'.format('' if p == -1 else '.' + str(p))).format(value)
    m = RE_FLOAT_TRIM.match(string)
    if m:
        string = m.group('keep')
        if m.group('keep2'):
            string += m.group('keep2')
    return string


def round_half_up(n, scale=0):
    """Round half up."""

    mult = 10 ** scale
    return math.floor(n * mult + 0.5) / mult
