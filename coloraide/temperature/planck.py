"""
Planckian curve.

https://en.wikipedia.org/wiki/Planckian_locus#The_Planckian_locus_in_the_XYZ_color_space
"""
from __future__ import annotations
import math
from ..types import VectorLike, Vector
from .. import util


# Constants for Planck's Law
H = 6.62607015e-34 * 1e18  # Plank's constant: `nm2 kg / s`
C = 299792458 * 1e9  # Speed of light: `nm / s`
K = 1.380649e-23 * 1e18  # Boltzmann constant: `nm2 kg s-2 K-1`
C1 = 2 * math.pi * H * C ** 2  # First radiation constant
C2 = (H * C) / K  # Second radiation constant


def temp_to_uv_planckian_locus(
    temp: float,
    cmfs: dict[int, tuple[float, float, float]],
    white: VectorLike,
    start: int = 360,
    end: int = 830,
    step: int = 5
) -> Vector:
    """
    Temperature to Planckian locus.

    https://en.wikipedia.org/wiki/Planckian_locus#The_Planckian_locus_in_the_XYZ_color_space
    """
    x = y = z = 0.0

    for wavelength in range(start, end + 1, step):
        m = C1 * (wavelength ** -5) * (math.exp(C2 / (wavelength * temp)) - 1.0) ** -1
        x += m * cmfs[wavelength][0]
        y += m * cmfs[wavelength][1]
        z += m * cmfs[wavelength][2]

    return util.xy_to_uv_1960(util.xyz_to_xyY([x, y, z], white)[:2])
