"""
RYB color space.

Gosset and Chen
http://bahamas10.github.io/ryb/assets/ryb.pdf
"""
from __future__ import annotations
import math
from .. import util
from . import Prism, Space
from .. import algebra as alg
from ..channels import Channel
from ..cat import WHITES
from ..easing import _solve_bezier, _bezier
from ..types import Vector, Matrix

# RYB corners that correspond to the RGB cube map
RYB_MAP = alg.transpose(
    [
        [0.0, 0.0, 0.0],  # White
        [1.0, 0.0, 0.0],  # Red
        [0.0, 1.0, 0.0],  # Yellow
        [1.0, 1.0, 0.0],  # Orange
        [0.0, 0.0, 1.0],  # Blue
        [1.0, 0.0, 1.0],  # Violet
        [0.0, 1.0, 1.0],  # Green
        [1.0, 1.0, 1.0]   # Black
    ]
)

# In terms of RGB
GOSSET_CHEN_CUBE = alg.transpose(
    [
        [1.0, 1.0, 1.0],      # White (c000)
        [1.0, 0.0, 0.0],      # Red (c100)
        [1.0, 1.0, 0.0],      # Yellow (C010)
        [1.0, 0.5, 0.0],      # Orange (c110)
        [0.163, 0.373, 0.6],  # Blue (c001)
        [0.5, 0.0, 0.5],      # Violet (c101)
        [0.0, 0.66, 0.2],     # Green (c011)
        [0.2, 0.094, 0.0]     # Black (c111)
    ]
)

SMOOTH_STEP_COEFF = (-2, 3, 0)
cubic_poly = _bezier(*SMOOTH_STEP_COEFF)


def barycentric_guess(cube: Matrix, target: Vector) -> Vector:
    """
    Weight each corner by inverse physical distance to the target.

    Bias the guess toward the corner/edge the target is actually near.
    """

    r, g, b = target
    # Inverse distance of target from corners in respect to RGB coordinates
    d_inv = [
        alg.zdiv(1.0, math.sqrt(d_rgb[0] ** 2 + d_rgb[1] ** 2 + d_rgb[2] ** 2), 1e12)
        for d_rgb in [[cube[0][i] - r, cube[1][i] - g, cube[2][i] - b] for i in range(8)]
    ]
    # Create weights we can apply to the coordinate corners
    s = sum(d_inv)
    w = [v / s for v in d_inv]

    # Calculate a RYB guess based on where the RGB color is in relation to the RYB corners.
    return [alg.clamp(guess, 0.0, 1.0) for guess in alg.matmul(RYB_MAP, w, dims=alg.D2_D1)]


def srgb_to_ryb(rgb: Vector, cube_t: Matrix, biased: bool) -> Vector:
    """Convert RYB to sRGB."""

    # Improve inverse trilinear interpolation by weighting
    # the initial guess towards the closest corner/edge.
    guess = barycentric_guess(cube_t, rgb)

    # Calculate the RYB value
    ryb = alg.ilerp3d(cube_t, rgb, guess=guess, tol=1e-15)
    # Remove smoothstep easing if "biased" is enabled.
    return [_solve_bezier(t, *SMOOTH_STEP_COEFF) if 0 <= t <= 1 else t for t in ryb] if biased else ryb


def ryb_to_srgb(ryb: Vector, cube_t: Matrix, biased: bool) -> Vector:
    """Convert RYB to sRGB."""

    # Apply cubic easing function
    if biased:
        ryb = [cubic_poly(t) if 0 <= t <= 1 else t for t in ryb]
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

        return ryb_to_srgb(coords, self.RYB_CUBE, self.BIASED)

    def from_base(self, coords: Vector) -> Vector:
        """From sRGB."""

        return srgb_to_ryb(coords, self.RYB_CUBE, self.BIASED)


class RYBBiased(RYB):
    """
    Gosset and Chen RYB with biasing towards the vertices.

    This mimics exactly what was done in the paper.
    """

    NAME = "ryb-biased"
    SERIALIZE = ("--ryb-biased",)
    BIASED = True
