"""
Calculate CCT with Robertson 1968 method.

Uses Robertson 1968 method.

- https://en.wikipedia.org/wiki/Correlated_color_temperature#Robertson's_method
- http://www.brucelindbloom.com/index.html?Math.html
"""
from __future__ import annotations
import math
from .. import algebra as alg
from .. import util
from ..temperature import CCT
from ..types import Vector
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


# Table for Robertson 1968 method
# Data: reciprocal temperature, u, v, slope
RUVT = [
    (0.0, 0.18006, 0.26352, -0.24341),
    (10.0, 0.18066, 0.26589, -0.25479),
    (20.0, 0.18133, 0.26846, -0.26876),
    (30.0, 0.18208, 0.27119, -0.28539),
    (40.0, 0.18293, 0.27407, -0.30470),
    (50.0, 0.18388, 0.27709, -0.32675),
    (60.0, 0.18494, 0.28021, -0.35156),
    (70.0, 0.18611, 0.28342, -0.37915),
    (80.0, 0.18740, 0.28668, -0.40955),
    (90.0, 0.18880, 0.28997, -0.44278),
    (100.0, 0.19032, 0.29326, -0.47888),
    (125.0, 0.19462, 0.30141, -0.58204),
    (150.0, 0.19962, 0.30921, -0.70471),
    (175.0, 0.20525, 0.31647, -0.84901),
    (200.0, 0.21142, 0.32312, -1.0182),
    (225.0, 0.21807, 0.32909, -1.2168),
    (250.0, 0.22511, 0.33439, -1.4512),
    (275.0, 0.23247, 0.33904, -1.7298),
    (300.0, 0.24010, 0.34308, -2.0637),
    (325.0, 0.24792, 0.34655, -2.4681),  # Note: 0.24792 is a corrected value for the error found in W&S as 0.24702
    (350.0, 0.25591, 0.34951, -2.9641),
    (375.0, 0.26400, 0.35200, -3.5814),
    (400.0, 0.27218, 0.35407, -4.3633),
    (425.0, 0.28039, 0.35577, -5.3762),
    (450.0, 0.28863, 0.35714, -6.7262),
    (475.0, 0.29685, 0.35823, -8.5955),
    (500.0, 0.30505, 0.35907, -11.324),
    (525.0, 0.31320, 0.35968, -15.628),
    (550.0, 0.32129, 0.36011, -23.325),
    (575.0, 0.32931, 0.36038, -40.770),
    (600.0, 0.33724, 0.36051, -116.45)
]


class Robertson1968(CCT):
    """Delta E plugin class."""

    NAME = 'robertson-1968'

    def to_cct(self, color: Color, **kwargs: Any) -> Vector:
        """Calculate a color's CCT."""

        u, v = color.uv('1960')

        # Search for line pair coordinate is between.
        previous_di = temp = duv = 0.0
        end = len(RUVT) - 1

        for index, current in enumerate(RUVT):
            # Get the distance
            di = (v - current[2]) - current[3] * (u - current[1])
            if index > 0 and (di <= 0.0 or index == end):
                # Calculate the required interpolation factor between the two lines
                previous = RUVT[index - 1]
                current_denom = math.sqrt(1.0 + current[3] ** 2)
                di /= current_denom
                previous_denom = math.sqrt(1.0 + previous[3] ** 2)
                dip = previous_di / previous_denom
                factor = dip / (dip - di)

                # Calculate the temperature, if the mired value is zero
                # assume the maximum temperature of 100000K.
                mired = alg.lerp(previous[0], current[0], factor)
                temp = 1.0E6 / mired if mired > 0 else float('inf')

                # Interpolate the slope vectors
                dup = 1 / previous_denom
                dvp = previous[3] / previous_denom
                du = 1 / current_denom
                dv = current[3] / current_denom
                du = alg.lerp(dup, du, factor)
                dv = alg.lerp(dvp, dv, factor)
                denom = math.sqrt(du ** 2 + dv ** 2)
                du /= denom
                dv /= denom

                # Calculate Duv
                duv = (
                    du * (u - alg.lerp(previous[1], current[1], factor)) +
                    dv * (v - alg.lerp(previous[2], current[2], factor))
                )

                break

            # Save distance as previous
            previous_di = di

        return [temp, -duv if duv else duv]

    def from_cct(self, color: type[Color], kelvin: float, duv: float = 0.0, **kwargs: Any) -> Color:
        """Calculate a color that satisfies the CCT."""

        # Find inverse temperature to use as index.
        r = 1.0E6 / kelvin
        u = v = 0.0
        end = len(RUVT) - 2

        for index, current in enumerate(RUVT):
            future = RUVT[index + 1]

            # Find the two isotherms that our target temp is between
            if r < future[0] or index == end:
                # Find relative weight between the two values
                f = (future[0] - r) / (future[0] - current[0])

                # Interpolate the uv coordinates of our target temperature
                u = alg.lerp(future[1], current[1], f)
                v = alg.lerp(future[2], current[2], f)

                # Calculate the offset along the slope
                if duv:
                    # Calculate the slope vectors
                    u1 = 1.0
                    v1 = current[3]
                    length = math.sqrt(1.0 + v1 ** 2)
                    u1 /= length
                    v1 /= length

                    u2 = 1.0
                    v2 = future[3]
                    length = math.sqrt(1.0 + v2 ** 2)
                    u2 /= length
                    v2 /= length

                    # Find vector from the locus to our point.
                    du = alg.lerp(u2, u1, f)
                    dv = alg.lerp(v2, v1, f)
                    denom = math.sqrt(du ** 2 + dv ** 2)
                    du /= denom
                    dv /= denom

                    # Adjust the uv by the calculated offset
                    u += du * -duv
                    v += dv * -duv
                break

        return color('xyz-d65', util.xy_to_xyz(util.uv_1960_to_xy([u, v]), 1))
