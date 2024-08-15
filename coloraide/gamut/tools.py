"""Common gamut related tools."""
from __future__ import annotations
import math
from .. import algebra as alg


def adaptive_hue_independent(l: float, c: float, alpha: float = 0.05) -> float:
    """
    Calculate a hue independent lightness anchor for the chroma compression.

    https://bottosson.github.io/posts/gamutclipping/#adaptive-%2C-hue-independent

    Copyright (c) 2021 Björn Ottosson

    Permission is hereby granted, free of charge, to any person obtaining a copy of
    this software and associated documentation files (the "Software"), to deal in
    the Software without restriction, including without limitation the rights to
    use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
    of the Software, and to permit persons to whom the Software is furnished to do
    so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    """

    ld = l - 0.5
    abs_ld = abs(ld)
    e1 = 0.5 + abs_ld + alpha * c
    return 0.5 * (1 + alg.sign(ld) * (e1 - math.sqrt(e1 ** 2 - 2.0 * abs_ld)))
