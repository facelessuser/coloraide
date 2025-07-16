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
from dataclasses import dataclass

if TYPE_CHECKING:  #pragma: no cover
    from ..color import Color

# Original 31 mired points 0 - 600
MIRED_ORIGINAL = tuple(range(0, 100, 10)) + tuple(range(100, 601, 25))
# Extended 16 mired points 625 - 1000
MIRED_EXTENDED = MIRED_ORIGINAL + tuple(range(625, 1001, 25))


@dataclass(frozen=True)
class CCTEntry:
    """CCT LUT entry."""

    mired: float
    u: float
    v: float
    slope: float
    slope_length: float
    du: float
    dv: float


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
    ) -> list[CCTEntry]:
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

        Additionally, we precalculate a few other things to save time:
        - slope length of unit vector
        - u component of slope unit vector
        - v component of slope unit vector
        """

        xyzw = util.xy_to_xyz(white)
        table = []  # type: list[CCTEntry]
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

            # Attempt to calculate the slope, if it falls exactly where the slope switch,
            # There will be a divide by zero, just skip this location.
            try:
                m1 = -((uv[1] - uv1[1]) / (uv[0] - uv1[0])) ** -1
                m2 = -((uv2[1] - uv[1]) / (uv2[0] - uv[0])) ** -1
            except ZeroDivisionError:  # pragma: no cover
                continue

            m = alg.lerp(m1, m2, factor)
            if sigfig:
                template = f'{{:.{sigfig}g}}'
                slope = float(template.format(m))
                length = math.sqrt(1 + slope * slope)

                table.append(
                    CCTEntry(
                        float(t),
                        float(template.format(uv[0])),
                        float(template.format(uv[1])),
                        slope,
                        length,
                        1 / length,
                        slope / length
                    )
                )
            else:
                length = math.sqrt(1 + m * m)
                table.append(CCTEntry(t, uv[0], uv[1], m, length, 1 / length, m / length))
        return table

    def calc_du_dv(
        self,
        previous: CCTEntry,
        current: CCTEntry,
        factor: float
    ) -> tuple[float, float]:
        """Calculate the Duv."""

        pslope = previous.slope
        slope = current.slope
        u1 = previous.du
        v1 = previous.dv
        u2 = current.du
        v2 = current.dv

        # Check for discontinuity and adjust accordingly
        if (pslope * slope) < 0:
            u2 *= -1
            v2 *= -1

        # Find vector from the locus to our point.
        du = alg.lerp(u2, u1, factor)
        dv = alg.lerp(v2, v1, factor)
        length = math.sqrt(du ** 2 + dv ** 2)
        du /= length
        dv /= length

        return du, dv

    def to_cct(self, color: Color, **kwargs: Any) -> Vector:
        """Calculate a color's CCT."""

        dip = kelvin = duv = 0.0
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
            slope = current.slope
            if slope < 0:
                di = (v - current.v) - slope * (u - current.u)
            else:
                di = (current.v - v) - slope * (current.u - u)

            if index > 0 and (di <= 0.0 or index == end):
                # Calculate the required interpolation factor between the two lines
                previous = self.table[index - 1]
                di /= current.slope_length
                dip /= previous.slope_length
                factor = dip / (dip - di)

                # Calculate the temperature. If the mired value is zero, assume infinity.
                pmired = previous.mired
                mired = (pmired - factor * (pmired - current.mired))
                kelvin = 1.0E6 / mired if mired else math.inf

                # Calculate Duv
                du, dv = self.calc_du_dv(previous, current, 1 - factor)
                duv = sign * (
                    du * (u - alg.lerp(previous.u, current.u, factor)) +
                    dv * (v - alg.lerp(previous.v, current.v, factor))
                )

                break

            # Save distance as previous
            dip = di

        return [kelvin, duv]

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
        mired = 1.0E6 / kelvin
        u = v = 0.0
        end = len(self.table) - 2

        for index, current in enumerate(self.table):
            future = self.table[index + 1]

            # Find the two isotherms that our target temp is between
            future_mired = future.mired
            if mired < future_mired or index == end:
                # Find relative weight between the two values
                f = (future_mired - mired) / (future_mired - current.mired)

                # Interpolate the uv coordinates of our target temperature
                u = alg.lerp(future.u, current.u, f)
                v = alg.lerp(future.v, current.v, f)

                # Calculate the offset along the slope
                if duv:
                    # Calculate the sign
                    slope = future.slope
                    sign = 1.0 if not (slope * current.slope) < 0 and slope >= 0 else -1.0

                    # Adjust the uv by the calculated offset
                    du, dv = self.calc_du_dv(current, future, f)
                    u += du * sign * duv
                    v += dv * sign * duv
                break

        return color.chromaticity(space, [u, v, 1], self.CHROMATICITY, scale=scale, scale_space=scale_space)
