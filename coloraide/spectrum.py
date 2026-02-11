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
LOCUS_START = 360
LOCUS_END = 780
LOCUS_STEP = 1


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
        angle = (alg.rect_to_polar(*norm)[1] - offset) % 360
        if angle == 0:
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

    # Achromatic, no wavelength
    if all(abs(a - b) < 1e-12 for a, b in zip(xy, white)):
        return w1, dominant, complementary

    # Look for first intersection of the line drawn through the white point
    # and the current color with the spectral locus. Check the dominant and
    # complementary, but return as soon as we have the dominant. If no dominant
    # is found, we'll use the complementary.
    locus = [util.xyz_to_xyY(cmfs.CIE_1931_2DEG[r], white)[:-1] for r in range(LOCUS_START, LOCUS_END + 1, LOCUS_STEP)]
    start = xy_to_angle(locus[0], white)
    current = xy_to_angle(xy, white, start, invert=reverse)
    invert = xy_to_angle(xy, white, start, invert=not reverse)
    found = [False, False]
    for i in range(0, len(locus) - 2):

        # Check if our angle is greater than the current locus point's angle
        a_next = xy_to_angle(locus[i], white, start)
        if a_next <= current and not found[0]:
            target = current
        elif a_next <= invert and not found[1]:
            target = invert
        else:
            continue

        # Get the intersection
        intersect = alg.line_intersect(white, xy, locus[i - 1], locus[i]) if a_next != target else locus[i]
        # Unlikely, but included for sanity
        if intersect is None:  # pragma: no cover
            continue

        # Use the intersection to estimate the interpolation factor for the wavelength,
        # and then get the interpolated value via Sprague interpolation.
        i0 = i - 1
        i2 = 0 if abs(locus[i0][0] - locus[i][0]) > abs(locus[i0][1] - locus[i][1]) else 1
        f = alg.ilerp(locus[i0][i2], locus[i][i2], intersect[i2])
        w = alg.lerp(LOCUS_START + i0, LOCUS_START + i, f)
        intersect = util.xyz_to_xyY(cmfs.CIE_1931_2DEG[w], white)[:-1]

        if target == current:
            dominant = intersect
            w1 = w
            found[0] = True
        else:
            complementary = intersect
            w2 = w
            found[1] = True

        if found[0]:
            break

    # Unlikely catastrophic failure
    if not any(found):  # pragma: no cover
        return w1, dominant, complementary

    # If dominant isn't found, it is on the line of purples; use complementary instead
    if not found[0]:
        pt = alg.line_intersect(white, xy, locus[0], locus[-1])
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
