"""Check if color is in Rösch-MacAdam color solid (MacAdam limits)."""
from __future__ import annotations
import bisect
from . import Gamut
from .. import util
from .. import algebra as alg
from ..cat import WHITES
from ..types import Matrix, VectorT, MatrixInt, StrictNumber
from .rosch_macadam_solid import LUT, LUMINANCE, HUE
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  #pragma: no cover
    from ..color import Color

XYw = WHITES['2deg']['D65']
XYZ_D65 = util.xy_to_xyz(WHITES['2deg']['D65'])


def macadam_limits(luminance: float | None = None) -> Matrix:
    """
    Calculate the visible Macadam limit boundary points for the given lightness.

    If no lightness is provided, calculate the maximum boundary.
    Result is returned as xyY coordinates (in the D65 illuminant).
    """

    # Maximum Pointer gamut boundary
    # For each hue, find the lightness/chroma point that is furthest away from the white point.
    if luminance is None:
        return [[*alg.add(alg.polar_to_rect(LUT[i][1], h), XYw), 1] for i, h in enumerate(HUE[:-1])]

    # Pointer gamut boundary at a given lightness
    # Return all the points for a given lightness
    elif LUMINANCE[0] <= luminance <= LUMINANCE[-1]:
        # Handle too low lightness inside tolerance
        li, lf = closest_lightness(luminance, LUMINANCE)
        chroma = [alg.lerp(row[li], row[li + 1], lf) for row in LUT[:-1]]
        return [[*alg.add(alg.polar_to_rect(c, h), XYw, dims=alg.D1), luminance] for c, h in zip(chroma, HUE[:-1])]

    # Luminance exceeds threshold
    else:
        raise ValueError(f'Luminance must be between {LUMINANCE[0]} and {LUMINANCE[-1]}, but was {luminance}')


def closest_lightness(l: float, lightness: VectorT[StrictNumber]) -> tuple[int, float]:
    """Calculate the two closest lightness values and return the first index and interpolation factor."""

    # Handle too low lightness inside tolerance
    if l <= lightness[0]:
        li = 0
        lf = 0.0

    # Handle too high lightness inside tolerance
    elif l >= lightness[-1]:
        li = len(lightness) - 2
        lf = 1.0

    # Handle lightness within gamut
    else:
        li = bisect.bisect(lightness, l) - 1
        l1, l2 = lightness[li:li + 2]
        lf = 1 - (l2 - l) / (l2 - l1)

    return li, lf


def closest_hue(h: float, hues: VectorT[StrictNumber]) -> tuple[int, float]:
    """Calculate the two closest hues and return the first index and interpolation factor."""

    # Handle hue at the start
    if h == hues[0]:  # pragma: no cover
        hi = 0
        hf = 0.0

    # Handle hue at the end
    elif h == hues[-1]:  # pragma: no cover
        hi = len(hues) - 2
        hf = 1.0

    # Handle all other hues
    else:
        hi = bisect.bisect(hues, h) - 1
        h1, h2 = hues[hi:hi + 2]
        hf = 1 - (h2 - h) / (h2 - h1)

    return hi, hf


class MacAdamLimits(Gamut):
    """The Rösch-MacAdam color solid (MacAdam limits)."""

    NAME = 'macadam-limits'
    LIGHTNESS = LUMINANCE
    HUE = HUE
    LUT: Matrix | MatrixInt = LUT

    def get_chroma_limit(self, l: float, h: float) -> float:
        """Get the chroma limit."""

        # Find the two closest lightness columns and calculate the needed interpolation factor.
        li, lf = closest_lightness(l, self.LIGHTNESS)

        # Find the two closest hue rows and calculate the needed interpolation factor.
        hi, hf = closest_hue(h, self.HUE)

        # Interpolate the chroma limit by interpolating chroma values for the closest lightness values and hues.
        row1, row2 = self.LUT[hi:hi + 2]
        return alg.lerp(alg.lerp(row1[li], row1[li + 1], lf), alg.lerp(row2[li], row2[li + 1], lf), hf)

    def in_gamut(self, color: Color, tolerance: float, **kwargs: Any) -> bool:
        """Test if in gamut."""

        # Convert to xyY
        xyz = (color.convert('xyz-d65', norm=False) if color.space() != 'xyz-d65' else color.normalize(nans=False))[:-1]
        x, y, Y = util.xyz_to_xyY(xyz, WHITES['2deg']['D65'])
        # Operate in a polar configuration
        c, h = alg.rect_to_polar(*alg.subtract((x, y), WHITES['2deg']['D65'], dims=alg.D1))

        # If lightness exceeds the acceptable range, then we are not in gamut
        if (Y < (self.LIGHTNESS[0] - tolerance)) or (Y > (self.LIGHTNESS[-1] + tolerance)):
            return False

        # Test that the color does not exceed the max chroma
        return c <= (self.get_chroma_limit(Y, h) + tolerance)

    def fit(self, color: Color, **kwargs: Any) -> None:
        """Fit to gamut."""

        # Convert to xyY
        xyz = (color.convert('xyz-d65', norm=False) if color.space() != 'xyz-d65' else color.normalize(nans=False))[:-1]
        x, y, Y = util.xyz_to_xyY(xyz, WHITES['2deg']['D65'])
        # Operate in a polar configuration
        c, h = alg.rect_to_polar(*alg.subtract((x, y), WHITES['2deg']['D65'], dims=alg.D1))

        # Clamp lightness
        new_Y = min(self.LIGHTNESS[-1], max(self.LIGHTNESS[0], Y))

        # Get optimal chromaticity points
        new_c = min(c, self.get_chroma_limit(Y, h))
        x, y = alg.add(alg.polar_to_rect(new_c, h), WHITES['2deg']['D65'], dims=alg.D1)

        # Check if we made any changes
        adjusted = Y != new_Y or c != new_c

        # Adjust original color only if a modification was made
        color.update(color.new('xyz-d65', util.xy_to_xyz((x, y), new_Y), color[-1])) if adjusted else color
