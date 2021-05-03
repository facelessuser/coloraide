"""
Delta E ITP.

https://kb.portrait.com/help/ictcp-color-difference-metric
"""
import math


def distance(color1, color2, scalar=720, **kwargs):
    """Delta E ITP color distance formula."""

    i1, t1, p1 = color1.convert('ictcp').coords()
    i2, t2, p2 = color2.convert('ictcp').coords()

    # Equation (1)
    return scalar * math.sqrt((i2 - i1) ** 2 + 0.25 * (t2 - t1) ** 2 + (p2 - p1) ** 2)
