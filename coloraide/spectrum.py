"""
Handle spectral related things.

- Calculations colors from/to wavelengths.
"""
from __future__ import annotations
import math
from . import algebra as alg
from . import util
from .types import Vector, VectorLike
from . import cat
from . import cmfs

WHITE = cat.WHITES['2deg']['E']
LOCUS_START = cmfs.CIE_1931_2DEG.start
LOCUS_END = cmfs.CIE_1931_2DEG.end
LOCUS_STEP = cmfs.CIE_1931_2DEG.step


def xy_to_angle(xy: VectorLike, white: VectorLike, offset: float = 0.0, invert: bool = False) -> float:
    """
    Translate xy to an angle with white being the origin.

    If offset is provided, make the angle relative to the offset angle.

    If invert is requested, we want to rotate the xy point 180 degrees.
    """

    norm = alg.subtract(xy, white, dims=alg.D1)
    if invert:
        norm = alg.multiply(norm, -1, dims=alg.D1_SC)
    if offset:
        angle = (alg.rect_to_polar(*norm)[1] - offset) % 360.0
        if angle < 1e-12:
            angle = 360.0
    else:
        angle = alg.rect_to_polar(*norm)[1]
    return angle


def closest_wavelength(
    xy: VectorLike,
    white: VectorLike = WHITE,
    reverse: bool = False,
    closest: bool = True
) -> tuple[float, Vector, Vector]:
    """
    Get the closest dominant wavelength.

    Both intersections are returned, even if the other is on the line of purple.
    The first point is always in the dominant direction. If the dominant cannot
    be found, the complementary will be used and indicated with a negative sign.

    If `reverse` is set, then the complementary wavelength is returned instead,
    with the points arranged favoring the complementary wavelength. If it cannot
    be found, the dominant wavelength is returned with a negative sign.

    If `closet` is set, wavelengths are rounded to the closest.
    """

    w1 = w2 = math.nan
    dominant = [math.nan, math.nan]
    complementary = [math.nan, math.nan]

    # The detection of precise segments is very sensitive in high wavelength areas.
    # Cycle the white chromaticity coordinates so that we are comparing against a
    # white with the usual error that is already present in all other colors.
    # The xy coordinates we are comparing against in the CMFs are so squished that
    # this actually makes a difference.
    white = util.xyz_to_xyY(util.xy_to_xyz(white))[:-1]

    # Achromatic, no wavelength
    if all(abs(a - b) < 1e-12 for a, b in zip(xy, white)):
        return w1, dominant, complementary

    # Look for first intersection of the line drawn through the white point
    # and the current color with the spectral locus. Check the dominant and
    # complementary, but return as soon as we have the dominant. If no dominant
    # is found, we'll use the complementary.
    locus = [util.xyz_to_xyY(cmfs.CIE_1931_2DEG[r])[:-1] for r in range(LOCUS_START, LOCUS_END + 1, LOCUS_STEP)]
    start = xy_to_angle(locus[0], white)
    current = xy_to_angle(xy, white, start)
    invert = xy_to_angle(xy, white, start, invert=True)
    found = [False, False]
    for i in range(1, len(locus) - 2):
        # Get the next locus point angle
        a_next = xy_to_angle(locus[i], white, start)

        # Check if our angle is greater than the current locus point's angle
        for j in range(0, 2):

            # If has already been found, skip
            target = invert if j else current
            if a_next > target or found[j]:
                continue

            # Previous index
            i0 = i - 1

            # Get the intersection
            if target == a_next:
                intersect = locus[i]  # type: Vector | None
            elif target == xy_to_angle(locus[i0], white, start):
                intersect = locus[i0]
            else:
                intersect = alg.ray_line_intersect(white, xy, locus[i0], locus[i])
            if intersect is None:  # pragma: no cover
                continue

            # Use the intersection to estimate the interpolation factor for the wavelength,
            # and then get the interpolated value via Sprague interpolation.
            i2 = 0 if abs(locus[i0][0] - locus[i][0]) > abs(locus[i0][1] - locus[i][1]) else 1
            f = alg.ilerp(locus[i0][i2], locus[i][i2], intersect[i2])
            w = alg.lerp(LOCUS_START + i0, LOCUS_START + i, f)
            intersect = util.xyz_to_xyY(cmfs.CIE_1931_2DEG[w], white)[:-1]

            if j == 0:
                dominant = intersect
                w1 = w
                found[j] = True
                if not reverse:
                    break
            else:
                complementary = intersect
                w2 = w
                found[j] = True
                if reverse:
                    break

        if found[reverse]:
            break

    # Unlikely catastrophic failure
    if not any(found):  # pragma: no cover
        return w1, dominant, complementary

    # Swap dominant and complementary if we are looking for complementary
    if reverse:
        dominant, complementary = complementary, dominant
        w1, w2 = w2, w1

    # If dominant isn't found, it is on the line of purples; use complementary instead
    if not found[reverse]:
        pt = alg.ray_line_intersect(white, xy, locus[0], locus[-1])
        # Shouldn't happen, but just in case
        if pt is not None:  # pragma: no cover
            dominant = pt
        w1 = -alg.round_half_up(w2) if closest else -w2
    else:
        complementary = dominant
        if closest:
            w1 = alg.round_half_up(w1)

    return w1, dominant, complementary


def wavelength_to_color(wavelength: float) -> Vector:
    """Return the XYZ value for the specified wavelength."""

    if wavelength < LOCUS_START or wavelength > LOCUS_END:
        raise ValueError(f'{wavelength}nm exceeds the range of {LOCUS_START}nm - {LOCUS_END}nm')

    # Wavelength is within the CMFs
    return cmfs.CIE_1931_2DEG[wavelength]
