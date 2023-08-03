"""
RYB color space.

Gosset and Chen
http://bahamas10.github.io/ryb/assets/ryb.pdf
"""
from ..spaces import Regular, Space
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


def apply_bias(ryb: Vector) -> Vector:
    """Apply bias towards corners."""

    return [-2 * t ** 3 + 3 * t ** 2 for t in ryb]


def remove_bias(ryb: Vector) -> Vector:
    """Remove the cubic bias using Newton's method."""

    new = []
    for c in ryb:
        target = c

        # Guessing properly is critical for good round tripping with fewest iterations.
        # Handle scenarios really close to our limits. Make larger guesses until we
        # get very closer to the upper bound.
        if abs(c) <= 1e-6:
            guess = 0.0
        elif abs(1 - c) < 1e-6:
            guess = 1.0
        elif 0 < c < 0.7:
            guess = c * 1.1
        else:
            guess = c

        last = float('nan')
        for _ in range(8):
            t1 = -2 * guess ** 3 + 3 * guess ** 2 - target
            t2 = -6 * guess ** 2 + 6 * guess

            if t2 == 0:
                break

            guess -= (t1 / t2)

            if guess == last:
                break

            last = guess
        new.append(guess)

    return new


def srgb_to_ryb(rgb: Vector, cube_t: Matrix, cube: Matrix, biased: bool) -> Vector:
    """Convert RYB to sRGB."""

    # Calculate the RYB value
    ryb = alg.ilerp3d(cube_t, rgb, vertices_t=cube)
    return remove_bias(ryb) if biased else ryb


def ryb_to_srgb(ryb: Vector, cube_t: Matrix, biased: bool) -> Vector:
    """Convert RYB to sRGB."""

    # Bias interpolation towards corners
    if biased:
        ryb = apply_bias(ryb)
    return alg.lerp3d(cube_t, ryb)


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
