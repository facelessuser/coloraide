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
from .fit_raytrace import get_conversion_matrices
from .. import util
from ..cat import WHITES, CAT
from .. import algebra as alg
from ..spaces import Space, RGBish
from ..types import VectorLike, Matrix
from ..spaces.oklab import OKLAB_TO_LMS3
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


def get_hue_data(name: str, cs: Space, cat: str, adapt: CAT, h: float) -> tuple[Matrix, float, list[float]]:
    """
    Get hue data.

    At fixed L and H, each linear RGB channel is exactly cubic in chroma c:

    ```
    channelᵢ(c) = Aᵢ·c³ + 3L·Bᵢ·c² + 3L²·Dᵢ·c + L³
    ```

    because `l'ₖ = L + Qₖ·c` is affine in c (the a, b axes enter Oklab→LMS
    linearly), and `channelᵢ = Σₖ Tᵢₖ·l'ₖ³`. The constant is `L³` since `c = 0` is
    gray and the rows of LMS to RGB sum to 1.
    """

    m = get_conversion_matrices(name, cs, cat, adapt)[0]
    rad = math.radians(h)
    q1, q2, q3 = alg.matmul_x3(
        OKLAB_TO_LMS3,
        [0, math.cos(rad), math.sin(rad)],
        dims=alg.D2_D1
    )
    m2 = alg.matmul_x3(
        m,
        [
            [q1 ** 3, q1 ** 2, q1],
            [q2 ** 3, q2 ** 2, q2],
            [q3 ** 3, q3 ** 2, q3]
        ],
        dims=alg.D2
    )

    # Substituting `c = L·t` factors L out entirely: `channelᵢ(c) = L³·Pᵢ(t)` with
    #
    # ```
    # Pᵢ(t) = Aᵢ·t³ + 3Bᵢ·t² + 3Dᵢ·t + 1
    # ```
    #
    # so `Pᵢ` - hence the lower-gamut exit and the monotonicity structure - depends
    # only on H and is pre-computed here, once per hue. Only the white bound stays
    # per color (it lands at `Pᵢ = L⁻³`); see compute.
    #
    # Lower exit: smallest `t > 0` where any channel reaches the black bound
    # (`channelᵢ = 0 ⟺ Pᵢ = 0`). Every channel starts at `Pᵢ(0) = 1`, so the first
    # such t is where the gamut is first left downward, whatever the lightness.
    t_lower = math.inf
    # First turning point of each channel in t-space (infinity if monotonic)
    turn = [0.0] * 3
    for i, v in enumerate(m2):
        t_lower = min(t_lower, first_root([v[0], 3 * v[1], 3 * v[2], 1], 1e-9, 1))
        turn[i] = first_root([0, v[0], 2 * v[1], v[2]], 1e-12, math.inf)
    return m2, t_lower, turn


@lru_cache(maxsize=1024)
def get_hue_data_cached(name: str, cs: Space, cat: str, adapt: CAT, h: float) -> tuple[Matrix, float, list[float]]:
    """Get hue data but use a hue_cache."""

    return get_hue_data(name, cs, cat, adapt, h)


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
            color.update('xyz-d65', [0, 0, 0], mapcolor[-1])
            return
        elif l >= 1:
            color.update('xyz-d65', WHITE, mapcolor[-1])
            return

        cat = color.CHROMATIC_ADAPTATION
        adapt = color.CAT_MAP[cat]
        m, t_lower, turn = (
            get_hue_data_cached(space, cs, cat, adapt, h) if cache else get_hue_data(space, cs, cat, adapt, h)
        )
        # Work in `t = c/L`. The cap starts at the input chroma and the (hue-only) lower
        # exit; the white bound below can only pull it lower.
        max_t = min(c / l, t_lower)
        target = 1 / (l ** 3)
        for i, v in enumerate(m):
            if turn[i] > max_t:
                if v[2] < 0:
                    continue
                p_max_t = ((v[0] * max_t + 3 * v[1]) * max_t + 3 * v[2]) * max_t + 1
                if p_max_t < target:
                    continue
            max_t = min(max_t, first_root([v[0], 3 * v[1], 3 * v[2], 1 - target], 1e-9, max_t))

        mapcolor[1] = l * max_t
        clip_channels(mapcolor.convert(orig_space, in_place=True))
        color.update(mapcolor)
