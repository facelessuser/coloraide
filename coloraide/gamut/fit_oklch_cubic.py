"""
Gamut mapping by using OkLCh and a cubic solver.

MIT License

Copyright (c) 2021 Lea Verou, Chris Lilley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

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
from __future__ import annotations
import math
from functools import lru_cache
from . import Fit, clip_channels
from .. import util
from ..cat import WHITES, calc_adaptation_matrices, Bradford
from .. import algebra as alg
from ..spaces import Space, RGBish
from ..types import Vector, VectorLike, Matrix
from ..spaces.oklab import LMS_TO_XYZD65, OKLAB_TO_LMS3
from typing import Any, TYPE_CHECKING  # noqa: F401

if TYPE_CHECKING:  #pragma: no cover
    from ..color import Color

WHITE = util.xy_to_xyz(WHITES['2deg']['D65'])


def first_root(coeff: VectorLike, mn: float, mx: float) -> float:
    """Get the best/smallest root that is within the specified range."""

    best = math.inf
    for r in alg.solve_poly(coeff):
        if mn < r < mx and r < best:
            best = r
    return best


def get_hue_data(name: str, cs: Space, h: float) -> tuple[Vector, Vector, Vector, float, list[float]]:
    """
    Get hue data.

    At fixed L and H, each linear RGB channel is exactly cubic in chroma c:

    ```
    channelᵢ(c) = L³ + 3L²·Aᵢ·c + 3L·Bᵢ·c² + Dᵢ·c³
    ```

    because `l'ₖ = L + Qₖ·c` is affine in c (the a, b axes enter Oklab→LMS
    linearly), and `channelᵢ = Σₖ Tᵢₖ·l'ₖ³`. The constant is `L³` since `c = 0` is
    gray and the rows of LMS to RGB sum to 1.
    """

    m = get_lms_to_rgb(name, cs)
    rad = math.radians(h)
    q = alg.matmul_x3(OKLAB_TO_LMS3, [0, math.cos(rad), math.sin(rad)], dims=alg.D2_D1)
    a = alg.matmul_x3(m, q, dims=alg.D2_D1)
    b = alg.matmul_x3(m, [x * x for x in q], dims=alg.D2_D1)
    d = alg.matmul_x3(m, [x ** 3 for x in q], dims=alg.D2_D1)

    # Substituting `c = L·t` factors L out entirely: `channelᵢ(c) = L³·Pᵢ(t)` with
    #
    # ```
    # Pᵢ(t) = 1 + 3Aᵢ·t + 3Bᵢ·t² + Dᵢ·t³
    # ```
    #
    # so `Pᵢ` — hence the lower-gamut exit and the monotonicity structure — depends
    # only on H and is pre-computed here, once per hue. Only the white bound stays
    # per color (it lands at `Pᵢ = L⁻³`); see compute.
    #
    # Lower exit: smallest `t > 0` where any channel reaches the black bound
    # (`channelᵢ = 0 ⟺ Pᵢ = 0`). Every channel starts at `Pᵢ(0) = 1`, so the first
    # such t is where the gamut is first left downward, whatever the lightness.
    t_lower = math.inf
    # First turning point of each channel in t-space (infinity if monotonic)
    turn = [0.0] * 3
    for i in range(3):
        t_lower = min(t_lower, first_root([d[i], 3 * b[i], 3 * a[i], 1], 1e-9, 1))
        turn[i] = first_root([0, d[i], 2 * b[i], a[i]], 1e-12, math.inf)
    return a, b, d, t_lower, turn


@lru_cache(maxsize=1024)
def get_hue_data_cached(name: str, cs: Space, h: float) -> tuple[Vector, Vector, Vector, float, list[float]]:
    """Get hue data but use a hue_cache."""

    return get_hue_data(name, cs, h)


@lru_cache(maxsize=10)
def get_lms_to_rgb(name: str, space: Space) -> Matrix:
    """Get LMS to RGB matrix."""

    m = space.TO_RGB  # type: ignore[attr-defined]
    if space.WHITE != WHITES['2deg']['D65']:
        m = alg.matmul_x3(
            m,
            calc_adaptation_matrices(WHITES['2deg']['D65'], space.WHITE, Bradford.MATRIX),
            dims=alg.D2
        )
    return alg.matmul_x3(m, LMS_TO_XYZD65, dims=alg.D2)


class OkLChCubic(Fit):
    """
    Gamut mapping by using a OkLCh cubic solver.

    It is based on the observation that at fixed L and H each linear-P3 channel is exactly a cubic equation in chroma
    (l' is affine in C, then cubed), so the C boundary is the smallest chroma at which any channel reaches 0 or 1 -
    found via standard closed form cubic equation solving formulas and optimized further through some observations about
    the types of equations produced and a lazily populated hue cache (which is not necessary, just an additional
    optimization).

    We apply this approach to all linear gamuts.
    """

    NAME = "oklch-cubic"

    def fit(
        self,
        color: Color,
        space: str,
        *,
        cache: bool = False,
        clear_cache: bool = False,
        **kwargs: Any
    ) -> None:
        """Scale the color within its gamut but preserve L and h as much as possible."""

        orig_space = space
        cs = color.CS_MAP[space]

        if clear_cache:
            get_hue_data_cached.cache_clear()

        # If there is a linear version of the RGB space, results will be better if we use that.
        # Recalculate the bounding box relative to the linear version.
        linear = cs.linear()
        if linear and linear in color.CS_MAP:
            space = linear
            cs = color.CS_MAP[space]

        if not isinstance(cs, RGBish) or not hasattr(cs, 'TO_RGB'):
            raise ValueError(f"'{space}' is not supported in OkLCh Cubic")

        orig = color.space()
        mapcolor = color.convert('oklch', norm=False) if orig != 'oklch' else color.clone().normalize(nans=False)
        l, c, h = mapcolor[:-1]

        if l <= 0:
            color.update('xyz-d65', [0, 0, 0])
            return
        elif l >= 1:
            color.update('xyz-d65', WHITE)
            return

        a, b, d, t_lower, turn = get_hue_data_cached(space, cs, h) if cache else get_hue_data(space, cs, h)
        # Work in `t = c/L`. The cap starts at the input chroma and the (hue-only) lower
        # exit; the white bound below can only pull it lower.
        max_t = min(c / l, t_lower)
        target = 1 / (l ** 3)
        for i in range(3):
            if turn[i] > max_t:
                if a[i] < 0:
                    continue
                p_max_t = ((d[i] * max_t + 3 * b[i]) * max_t + 3 * a[i]) * max_t + 1
                if p_max_t < target:
                    continue
            max_t = min(max_t, first_root([d[i], 3 * b[i], 3 * a[i], 1 - target], 1e-9, max_t))

        mapcolor[1] = l * max_t
        clip_channels(mapcolor.convert(orig_space, in_place=True))
        color.update(mapcolor)
