"""
RYB color space.

Gosset and Chen
http://bahamas10.github.io/ryb/assets/ryb.pdf
"""
from __future__ import annotations
import math
from .. import util
from ..spaces import Prism, Space
from .. import algebra as alg
from ..channels import Channel
from ..cat import WHITES
from ..types import Vector, Matrix

# In terms of RGB
GOSSET_CHEN_CUBE = [
    [1.0, 1.0, 1.0],      # White (c000)
    [1.0, 0.0, 0.0],      # Red (c100)
    [1.0, 1.0, 0.0],      # Yellow (C010)
    [1.0, 0.5, 0.0],      # Orange (c110)
    [0.163, 0.373, 0.6],  # Blue (c001)
    [0.5, 0.0, 0.5],      # Violet (c101)
    [0.0, 0.66, 0.2],     # Green (c011)
    [0.2, 0.094, 0.0]     # Black (c111)
]  # type: Matrix


def cubic_poly(t: float, a: float, b: float, c: float, d: float) -> float:
    """Cubic polynomial."""

    return a * t ** 3 + b * t ** 2 + c * t + d


def cubic_poly_dt(t: float, a: float, b: float, c: float) -> float:
    """Derivative of cubic polynomial."""

    return 3 * a * t ** 2 + 2 * b * t + c


def solve_cubic_poly(a: float, b: float, c: float, d: float) -> float:
    """
    Solve curve to find a `t` that satisfies our desired `x`.

    Using `alg.solve_poly` is actually faster and more accurate as it is an
    analytical approach. Since we are using Newton's method for the inverse
    trilinear interpolation, which is only accurate to around 1e-6 in our case,
    applying a very accurate cubic solver to a not so accurate inverse interpolation
    can actually give us an even more inaccurate result. This is evident in our use
    case around RYB [1, 1, 0] which can drop to around 1e-3 accuracy.

    Using an approach where we can better control accuracy and limit it to a similar accuracy
    of 1e-6 actually helps us maintain a minimum of 1e-6 accuracy through the sRGB
    gamut giving more consistent results within the trilinear cube.
    """

    eps = 1e-6
    maxiter = 8

    if d <= 0.0 or d >= 1.0:
        return d

    # Try Newtons method to see if we can find a suitable value
    f0 = lambda t: cubic_poly(t, a, b, c, -d)
    dx = lambda t: cubic_poly_dt(t, a, b, c)
    t, converged = alg.solve_newton(0.5, f0, dx, maxiter=maxiter, atol=eps)

    # We converged or we are close enough
    if converged:
        return t

    # Fallback to bisection
    return alg.solve_bisect(0.0, 1.0, f0, start=d, atol=eps)[0]


def srgb_to_ryb(rgb: Vector, cube_t: Matrix, cube: Matrix, biased: bool) -> Vector:
    """Convert RYB to sRGB."""

    # Calculate the RYB value
    ryb = alg.ilerp3d(cube_t, rgb, vertices_t=cube)
    # Remove smoothstep easing if "biased" is enabled.
    return [solve_cubic_poly(-2.0, 3.0, 0.0, t) if 0 <= t <= 1 else t for t in ryb] if biased else ryb


def ryb_to_srgb(ryb: Vector, cube_t: Matrix, biased: bool) -> Vector:
    """Convert RYB to sRGB."""

    # Apply cubic easing function
    if biased:
        ryb = [cubic_poly(t, -2.0, 3.0, 0.0, 0.0) if 0 <= t <= 1 else t for t in ryb]
    # Bias interpolation towards corners if "biased" enable. Bias is a smoothstep easing function.
    return alg.lerp3d(cube_t, ryb)


class RYB(Prism, Space):
    """
    The RYB color space based on the paper by Gosset and Chen.

    The easing function for biasing colors towards the vertices is not handled in this color space.
    """

    NAME = "ryb"
    BASE = "srgb"
    SERIALIZE = ("--ryb",)
    CHANNELS = (
        Channel("r", 0.0, 1.0, bound=True),
        Channel("y", 0.0, 1.0, bound=True),
        Channel("b", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "red": 'r',
        "yellow": 'y',
        "blue": 'b'
    }
    WHITE = WHITES['2deg']['D65']
    RYB_CUBE = GOSSET_CHEN_CUBE
    RYB_CUBE_T = alg.transpose(RYB_CUBE)
    BIASED = False
    SUBTRACTIVE = True

    def is_achromatic(self, coords: Vector) -> bool:
        """
        Test if color is achromatic.

        Achromatic colors in the traditional sense is just brown in RYB,
        so convert to RGB where it is easier to determine an actual achromatic color.
        """

        coords = self.to_base(coords)
        for x in alg.vcross(coords, [1, 1, 1]):
            if not math.isclose(0.0, x, abs_tol=util.ACHROMATIC_THRESHOLD):
                return False
        return True

    def to_base(self, coords: Vector) -> Vector:
        """To sRGB."""

        return ryb_to_srgb(coords, self.RYB_CUBE_T, self.BIASED)

    def from_base(self, coords: Vector) -> Vector:
        """From sRGB."""

        return srgb_to_ryb(coords, self.RYB_CUBE_T, self.RYB_CUBE, self.BIASED)


class RYBBiased(RYB):
    """
    Gosset and Chen RYB with biasing towards the vertices.

    This mimics exactly what was done in the paper.
    """

    NAME = "ryb-biased"
    SERIALIZE = ("--ryb-biased",)
    BIASED = True
