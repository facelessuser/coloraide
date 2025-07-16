"""
Calculate CCT with Robertson 1968 method.

Uses Robertson 1968 method.

- https://en.wikipedia.org/wiki/Correlated_color_temperature#Robertson's_method
- http://www.brucelindbloom.com/index.html?Math.html
"""
from __future__ import annotations
import math
from . import planck
from .. import algebra as alg
from .. import util
from .. import cat
from .. import cmfs
from ..temperature import CCT
from ..types import Vector, VectorLike, AnyColor
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  #pragma: no cover
    from ..color import Color

# Original 31 mired points 0 - 600
MIRED_ORIGINAL = tuple(range(0, 100, 10)) + tuple(range(100, 601, 25))
# Extended 16 mired points 625 - 1000
MIRED_EXTENDED = MIRED_ORIGINAL + tuple(range(625, 1001, 25))


class Robertson1968(CCT):
    """Delta E plugin class."""

    NAME = 'robertson-1968'
    CHROMATICITY = 'uv-1960'

    def __init__(
        self,
        cmfs: dict[int, tuple[float, float, float]] = cmfs.CIE_1931_2DEG,
        white: VectorLike = cat.WHITES['2deg']['D65'],
        mired: VectorLike = MIRED_EXTENDED,
        sigfig: int = 5,
        planck_step: int = 1,
    ) -> None:
        """Initialize."""

        self.white = white
        self.table = self.generate_table(cmfs, white, mired, sigfig, planck_step)

    def generate_table(
        self,
        cmfs: dict[int, tuple[float, float, float]],
        white: VectorLike,
        mired: VectorLike,
        sigfig: int,
        planck_step: int,
    ) -> list[tuple[float, float, float, float]]:
        """
        Generate the necessary table for the Robertson1968 method.

        The below algorithm, coupled with the 1nm CMFs for the 1931 2 degree table, allows us to replicate the
        documented 31 points exactly.

        For each mired value we calculate two additional points, one on each side at a distance of 0.1.
        We use a very small distance so that we can approximate the slope. We calculate the distance between
        the targeted value and the two neighbors and then calculate the slope of the two small lines. Then we
        can calculate an interpolation factor and interpolate the slope for our target.

        We are able to calculate the uv pair for each mired point directly except for 0. 0 requires us to
        interpolate the values as it will cause a divide by zero in the Planckian locus. In this case, we
        assume a perfect 0.5 (middle) for our interpolation.
        """

        xyzw = util.xy_to_xyz(white)
        table = []  # type: list[tuple[float, float, float, float]]
        to_uv = util.xy_to_uv_1960 if self.CHROMATICITY == 'uv-1960' else util.xy_to_uv
        for t in mired:
            uv1 = to_uv(planck.temp_to_xy_planckian_locus(1e6 / (t - 0.01), cmfs, xyzw, step=planck_step))
            uv2 = to_uv(planck.temp_to_xy_planckian_locus(1e6 / (t + 0.01), cmfs, xyzw, step=planck_step))
            if t == 0:
                factor = 0.5
                uv = [alg.lerp(uv1[0], uv2[0], factor), alg.lerp(uv1[1], uv2[1], factor)]
            else:
                uv = to_uv(planck.temp_to_xy_planckian_locus(1e6 / t, cmfs, xyzw, step=planck_step))
                d1 = math.sqrt((uv[1] - uv1[1]) ** 2 + (uv[0] - uv1[0]) ** 2)
                d2 = math.sqrt((uv2[1] - uv[1]) ** 2 + (uv2[0] - uv[0]) ** 2)
                factor = d1 / (d1 + d2)
            m1 = -((uv[1] - uv1[1]) / (uv[0] - uv1[0])) ** -1
            m2 = -((uv2[1] - uv[1]) / (uv2[0] - uv[0])) ** -1
            m = alg.lerp(m1, m2, factor)
            if sigfig:
                template = f'{{:.{sigfig}g}}'
                table.append(
                    (
                        float(t),
                        float(template.format(uv[0])),
                        float(template.format(uv[1])),
                        float(template.format(m))
                    )
                )
            else:
                table.append((t, uv[0], uv[1], m))
        return table

    def to_cct(self, color: Color, **kwargs: Any) -> Vector:
        """Calculate a color's CCT."""

        dip = temp = duv = 0.0
        sign = -1
        u, v = color.split_chromaticity(self.CHROMATICITY)[:-1]
        end = len(self.table) - 1

        # Search for line pair coordinate is between.
        for index, current in enumerate(self.table):
            # Get the distance
            # If a table was generated with values down to 1000K,
            # we would get a positive slope, so to keep logic the
            # same, adjust distance calculation such that negative
            # is still what we are looking for.
            slope = current[3]
            if slope < 0:
                di = (v - current[2]) - slope * (u - current[1])
            else:
                di = (current[2] - v) - slope * (current[1] - u)

            if index > 0 and (di <= 0.0 or index == end):
                # Calculate the required interpolation factor between the two lines
                previous = self.table[index - 1]
                pslope = previous[3]
                current_denom = math.sqrt(1.0 + slope ** 2)
                previous_denom = math.sqrt(1.0 + pslope ** 2)
                di /= current_denom
                dip /= previous_denom
                factor = dip / (dip - di)

                # Calculate the temperature, if the mired value is zero
                # assume the maximum temperature of 100000K.
                d = (previous[0] - factor * (previous[0] - current[0]))
                temp = 1.0E6 / d if d else math.inf

                # Angle
                a1 = math.atan2(pslope, 1) % math.tau
                a2 = math.atan2(slope, 1) % math.tau

                # Check slopes to see if we have a discontinuity and adjust
                if (slope * pslope) < 0:
                    a2 = (a2 + math.pi) if a2 < math.pi else (a2 - math.pi)

                # Find vector from the locus to our point.
                da = alg.lerp(a1, a2, factor)
                du, dv = math.cos(da), math.sin(da)

                # Calculate Duv
                duv = sign * (
                    du * (u - alg.lerp(previous[1], current[1], factor)) +
                    dv * (v - alg.lerp(previous[2], current[2], factor))
                )

                break

            # Save distance as previous
            dip = di

        return [temp, duv]

    def from_cct(
        self,
        color: type[AnyColor],
        space: str,
        kelvin: float,
        duv: float,
        scale: bool,
        scale_space: str | None,
        **kwargs: Any
    ) -> AnyColor:
        """Calculate a color that satisfies the CCT."""

        # Find inverse temperature to use as index.
        r = 1.0E6 / kelvin
        u = v = 0.0
        end = len(self.table) - 2

        for index, current in enumerate(self.table):
            future = self.table[index + 1]

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

                    # Check for discontinuity and adjust accordingly
                    discontinuity = (current[3] * future[3]) < 0
                    if discontinuity:
                        rad, ang = math.sqrt(u2 * u2 + v2 * v2), math.atan2(v2, u2) % math.tau
                        ang += math.pi
                        u2, v2 = rad * math.cos(ang), rad * math.sin(ang)

                    # Calculate the sign
                    sign = 1.0 if not discontinuity and future[3] >= 0 else -1.0

                    # Find vector from the locus to our point.
                    du = alg.lerp(u2, u1, f)
                    dv = alg.lerp(v2, v1, f)
                    denom = math.sqrt(du ** 2 + dv ** 2)
                    du /= denom
                    dv /= denom

                    # Adjust the uv by the calculated offset
                    u += du * sign * duv
                    v += dv * sign * duv
                break

        return color.chromaticity(space, [u, v, 1], self.CHROMATICITY, scale=scale, scale_space=scale_space)
