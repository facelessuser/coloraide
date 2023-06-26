"""
Planckian curve.

https://en.wikipedia.org/wiki/Planckian_locus#The_Planckian_locus_in_the_XYZ_color_space
"""
from __future__ import annotations
import math
from ..types import VectorLike, Vector
from .. import util

# Constants for Planck's Law
# Precise calculation
# ```
# H = 6.62607015e-34  # Plank's constant: `m2 kg / s`
# C = 299792458  # Speed of light: `m / s`
# K = 1.380649e-23  # Boltzmann constant: `m2 kg s-2 K-1`
# C1 = 2 * math.pi * H * C ** 2  # First radiation constant
# C2 = (H * C) / K  # Second radiation constant
# ```
# ITS-90 Standard rounds to 6 decimal places
C1 = 3.741771e-16
C2 = 1.4388e-2


def temp_to_xy_planckian_locus(
    temp: float,
    cmfs: dict[int, tuple[float, float, float]],
    white: VectorLike,
    start: int = 360,
    end: int = 830,
    step: int = 5,
    c1: float = C1,
    c2: float = C2
) -> Vector:
    """
    Temperature to Planckian locus.

    https://en.wikipedia.org/wiki/Planckian_locus#The_Planckian_locus_in_the_XYZ_color_space
    """
    x = y = z = 0.0

    for wavelength in range(start, end + 1, step):
        m = c1 * (wavelength ** -5) * math.expm1((c2 * 1e9) / (wavelength * temp)) ** -1
        cmf = cmfs[wavelength]
        x += m * cmf[0]
        y += m * cmf[1]
        z += m * cmf[2]

    return util.xyz_to_xyY([x, y, z], white)[:-1]
