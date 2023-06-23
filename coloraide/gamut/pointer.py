"""
Handle pointer gamut.

Data used for the gamut: https://www.rit-mcsl.org/UsefulData/PointerData.xls.
"""
from __future__ import annotations
import math
import bisect
from ..spaces.lab import xyz_to_lab, lab_to_xyz
from ..spaces.lch import lab_to_lch, lch_to_lab
from .. import algebra as alg
from .. import util
from ..types import Vector
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

# White point C as defined in the Pointer data spreadsheet
XYZ_W = (98.0722647623506, 100.0, 118.225418982695)
WHITE_POINT_SC = tuple(util.xyz_to_xyY(XYZ_W)[:-1])  # type: tuple[float, float]  # type: ignore[assignment]
# Rows: hue 0 - 350 at steps of 10
# Columns: lightness 15 - 90 at steps of 5
LCH_L = list(range(15, 91, 5))
LCH_H = list(range(0, 351, 10))
LCH_POINTER = [
    [10, 30, 43, 56, 68, 77, 79, 77, 72, 65, 57, 50, 40, 30, 19, 8],
    [15, 30, 45, 56, 64, 70, 73, 73, 71, 65, 57, 48, 39, 30, 18, 7],
    [14, 34, 49, 61, 69, 74, 76, 76, 74, 68, 61, 51, 40, 30, 19, 9],
    [35, 48, 59, 68, 75, 82, 84, 83, 80, 75, 67, 56, 45, 33, 21, 10],
    [27, 40, 53, 66, 79, 90, 94, 93, 88, 82, 72, 60, 47, 35, 22, 10],
    [10, 21, 34, 45, 60, 75, 90, 100, 102, 99, 88, 75, 59, 45, 30, 15],
    [4, 15, 26, 37, 48, 59, 70, 82, 93, 103, 106, 98, 85, 66, 45, 23],
    [5, 15, 25, 36, 46, 56, 67, 76, 85, 94, 102, 108, 103, 82, 58, 34],
    [6, 15, 24, 32, 40, 48, 55, 64, 72, 82, 94, 105, 115, 115, 83, 48],
    [4, 12, 20, 28, 36, 44, 53, 60, 68, 75, 83, 90, 98, 106, 111, 90],
    [9, 16, 23, 30, 37, 45, 51, 58, 65, 72, 80, 86, 94, 100, 106, 108],
    [9, 18, 27, 35, 44, 52, 59, 66, 74, 82, 87, 92, 95, 100, 96, 84],
    [4, 14, 23, 32, 41, 49, 57, 64, 71, 78, 84, 90, 94, 95, 83, 50],
    [5, 18, 30, 40, 48, 56, 64, 70, 77, 82, 85, 88, 89, 84, 64, 35],
    [7, 20, 32, 42, 52, 60, 69, 76, 82, 87, 89, 90, 83, 71, 54, 30],
    [7, 21, 34, 45, 57, 68, 75, 81, 84, 84, 83, 80, 72, 58, 44, 20],
    [8, 24, 36, 48, 58, 68, 76, 82, 85, 83, 78, 69, 59, 49, 34, 15],
    [13, 25, 36, 47, 57, 65, 70, 75, 76, 75, 71, 65, 57, 45, 30, 15],
    [10, 25, 38, 48, 57, 64, 69, 71, 72, 69, 64, 60, 51, 41, 29, 16],
    [7, 19, 30, 40, 48, 55, 59, 62, 62, 60, 55, 49, 41, 32, 23, 13],
    [5, 19, 29, 37, 42, 45, 46, 46, 45, 43, 39, 35, 30, 22, 14, 7],
    [0, 12, 17, 26, 34, 43, 49, 51, 54, 50, 46, 40, 32, 24, 14, 4],
    [2, 12, 20, 28, 35, 40, 45, 48, 51, 49, 45, 38, 32, 23, 15, 6],
    [10, 20, 29, 36, 42, 46, 49, 51, 52, 50, 45, 39, 32, 24, 15, 7],
    [8, 16, 26, 34, 41, 47, 49, 50, 50, 47, 42, 36, 29, 21, 12, 4],
    [9, 21, 32, 40, 49, 54, 55, 55, 52, 48, 43, 36, 29, 21, 13, 4],
    [12, 24, 34, 41, 46, 51, 55, 56, 51, 46, 40, 33, 27, 20, 13, 6],
    [14, 31, 42, 50, 55, 60, 60, 57, 50, 45, 39, 33, 26, 20, 13, 6],
    [10, 29, 45, 55, 60, 61, 60, 57, 53, 46, 40, 34, 25, 18, 11, 4],
    [20, 40, 60, 69, 71, 69, 65, 58, 50, 43, 36, 29, 24, 18, 12, 5],
    [30, 55, 72, 81, 79, 72, 64, 57, 50, 42, 35, 30, 24, 17, 12, 5],
    [62, 76, 85, 88, 85, 80, 71, 62, 55, 47, 41, 34, 27, 20, 14, 6],
    [60, 71, 79, 84, 85, 86, 82, 74, 66, 57, 48, 40, 31, 24, 16, 8],
    [20, 50, 72, 86, 89, 89, 86, 80, 72, 63, 54, 45, 36, 27, 18, 9],
    [26, 49, 63, 73, 82, 87, 87, 83, 78, 71, 62, 51, 40, 28, 18, 4],
    [15, 37, 52, 65, 73, 79, 82, 84, 79, 73, 63, 53, 40, 30, 17, 6]
]


def lch_sc_to_xyY(lch: Vector) -> Vector:
    """Convert from LCh to xy coordinates."""

    return util.xyz_to_xyY(lab_to_xyz(lch_to_lab(lch), XYZ_W), XYZ_W)


def to_lch_sc(color: Color) -> Vector:
    """Convert a color to LCh with an SC illuminant."""

    xyz = color.convert('xyz-d65').normalize(nans=False)
    xyz_sc = color.chromatic_adaptation(xyz._space.WHITE, WHITE_POINT_SC, xyz[:-1])
    return lab_to_lch(xyz_to_lab(xyz_sc, util.xy_to_xyz(WHITE_POINT_SC)))


def from_lch_sc(color: Color, lch: Vector) -> Color:
    """Convert a color from LCh with an SC illuminant."""

    xyz_sc = lab_to_xyz(lch_to_lab(lch), util.xy_to_xyz(WHITE_POINT_SC))
    xyz_d65 = color.chromatic_adaptation(WHITE_POINT_SC, color.CS_MAP['xyz-d65'].WHITE, xyz_sc)
    return color.update('xyz-d65', xyz_d65, color[-1])


def closest_lightness(l: float) -> tuple[int, float]:
    """Calculate the two closest lightness values and return the first index and interpolation factor."""

    # Handle too low lightness inside tolerance
    if l <= LCH_L[0]:
        li = 0
        lf = 0.0

    # Handle too high lightness inside tolerance
    elif l >= LCH_L[-1]:
        li = len(LCH_L) - 2
        lf = 1.0

    # Handle lightness with gamut
    else:
        li = bisect.bisect(LCH_L, l) - 1
        l1, l2 = LCH_L[li:li + 2]
        lf = 1 - (l2 - l) / (l2 - l1)

    return li, lf


def closest_hue(h: float) -> tuple[int, float]:
    """Calculate the two closest hues and return the first index and interpolation factor."""

    hi = 0
    # Handle wrapping hue
    if h > LCH_H[-1]:
        hi = len(LCH_H) - 1
        h1, h2 = 350, 360

    # Handle non-wrapping hue
    else:
        hi = bisect.bisect(LCH_H, h) - 1
        h1, h2 = LCH_H[hi:hi + 2]
    hf = 1 - (h2 - h) / (h2 - h1)

    return hi, hf


def get_chroma_limit(l: float, h: float) -> float:
    """Get the chroma limit."""

    # Find the two closest lightness columns and calculate the needed interpolation factor.
    li, lf = closest_lightness(l)

    # Find the two closest hue rows and calculate the needed interpolation factor.
    hi, hf = closest_hue(h)

    # Interpolate the chroma limit by interpolating chroma values for the closest lightness values and hues.
    if hi == len(LCH_H) - 1:
        row1, row2 = LCH_POINTER[-1], LCH_POINTER[0]
    else:
        row1, row2 = LCH_POINTER[hi:hi + 2]
    return alg.lerp(alg.lerp(row1[li], row1[li + 1], lf), alg.lerp(row2[li], row2[li + 1], lf), hf)


def fit_pointer_gamut(color: Color) -> Color:
    """Fit a color to the Pointer gamut."""

    # Convert to CIE LCh with the SC illuminant
    l, c, h = to_lch_sc(color)

    # Clamp lightness
    new_l = max(LCH_L[0], l)
    new_l = min(LCH_L[-1], new_l)

    new_c = min(c, get_chroma_limit(l, h))

    adjusted = l != new_l or c != new_c

    # Adjust original color only if a modification was made
    return from_lch_sc(color, [new_l, new_c, h]) if adjusted else color


def in_pointer_gamut(color: Color, tolerance: float) -> bool:
    """
    See if color is within the pointer gamut.

    Convert to CIE LCh using the SC illuminant.
    Find the closest hues and lightness (rows and columns) so we can interpolate
    the an appropriate max chroma for a given hue and lightness. Test that the
    color's chroma does not exceed the limit.
    """

    # Convert to CIE LCh with the SC illuminant
    l, c, h = to_lch_sc(color)

    # If lightness exceeds the acceptable range, then we are not in gamut
    if (l < (LCH_L[0] - tolerance)) or (l > (LCH_L[-1] + tolerance)):
        return False

    # Test that the color does not exceed the max chroma
    return c <= (get_chroma_limit(l, h) + tolerance)


def pointer_gamut_boundary(lightness: float | None = None) -> list[Vector]:
    """
    Calculate the Pointer gamut boundary points for the given lightness.

    If no lightness is provided, calculate the maximum pointer boundary.
    Result is returned as xyY coordinates (C illuminant).
    """

    # Maximum Pointer gamut boundary
    # For each hue, find the lightness/chroma point that is furthest away from the white point.
    if lightness is None:
        max_gamut = []  # type: list[Vector]
        for i, h in enumerate(LCH_H):
            max_dxy = 0.0
            max_xyy = [0.0, 0.0, 0.0]
            for j, l in enumerate(LCH_L):
                xyy = lch_sc_to_xyY([l, LCH_POINTER[i][j], h])
                dxy = math.sqrt((WHITE_POINT_SC[0] - xyy[0]) ** 2 + (WHITE_POINT_SC[1] - xyy[1]) ** 2)
                if dxy > max_dxy:
                    max_dxy = dxy
                    max_xyy = xyy
            max_gamut.append(max_xyy)
        return max_gamut

    # Pointer gamut boundary at a given lightness
    # Return all the points for a given lightness
    elif LCH_L[0] <= lightness <= LCH_L[-1]:
        li, lf = closest_lightness(lightness)
        chroma = [alg.lerp(row[li], row[li + 1], lf) for row in LCH_POINTER]
        return [lch_sc_to_xyY([lightness, c, h]) for c, h in zip(chroma, LCH_H)]

    # Lightness exceeds threshold
    else:
        raise ValueError('Lightness must be between {} and {}, but was {}'.format(LCH_L[0], LCH_L[-1], lightness))
