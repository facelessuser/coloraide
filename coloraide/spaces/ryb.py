"""
RYB color space.

Gosset and Chen
http://bahamas10.github.io/ryb/assets/ryb.pdf
"""
from __future__ import annotations
import math
from ..spaces import Regular, Space
from .. import algebra as alg
from ..channels import Channel
from ..cat import WHITES
from ..types import Vector, Matrix
from ..easing import _bezier, _solve_bezier

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


def srgb_to_ryb(rgb: Vector, cube_t: Matrix, cube: Matrix, biased: bool) -> Vector:
    """Convert RYB to sRGB."""

    # Calculate the RYB value
    ryb = alg.ilerp3d(cube_t, rgb, vertices_t=cube)
    # Remove smoothstep easing if "biased" is enabled.
    return [_solve_bezier(t, -2, 3, 0) if 0 <= t <= 1 else t for t in ryb] if biased else ryb


def ryb_to_srgb(ryb: Vector, cube_t: Matrix, biased: bool) -> Vector:
    """Convert RYB to sRGB."""

    # Bias interpolation towards corners if "biased" enable. Bias is a smoothstep easing function.
    return alg.lerp3d(cube_t, [_bezier(t, -2, 3, 0) if 0 <= t <= 1 else t for t in ryb] if biased else ryb)


class RYB(Regular, Space):
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

    def is_achromatic(self, coords: Vector) -> bool:
        """
        Test if color is achromatic.

        Achromatic colors in the traditional sense is just brown in RYB,
        so convert to RGB where it is easier to determine an actual achromatic color.
        """

        coords = self.to_base(coords)
        for x in alg.vcross(coords, [1, 1, 1]):
            if not math.isclose(0.0, x, abs_tol=1e-5):
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
