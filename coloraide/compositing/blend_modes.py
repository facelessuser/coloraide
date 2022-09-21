"""Blend modes."""
from __future__ import annotations
import math
from abc import ABCMeta, abstractmethod
from operator import itemgetter
from ..types import Vector


# -----------------------------------------
# Non-separable blending helper functions
# -----------------------------------------
def lum(rgb: Vector) -> float:
    """Get luminosity."""

    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def clip_color(rgb: Vector) -> Vector:
    """Clip color."""

    l = lum(rgb)
    n = min(*rgb)
    x = max(*rgb)

    if n < 0:
        rgb = [l + (((c - l) * l) / (l - n)) for c in rgb]

    if x > 1:
        rgb = [l + (((c - l) * (1 - l)) / (x - l)) for c in rgb]

    return rgb


def set_lum(rgb: Vector, l: float) -> Vector:
    """Set luminosity."""

    d = l - lum(rgb)
    new_rgb = [c + d for c in rgb]
    return clip_color(new_rgb)


def sat(rgb: Vector) -> float:
    """Saturation."""

    return max(*rgb) - min(*rgb)


def set_sat(rgb: Vector, s: float) -> Vector:
    """Set saturation."""

    final = [0.0] * 3
    indices, rgb_sort = zip(*sorted(enumerate(rgb), key=itemgetter(1)))
    if rgb_sort[2] > rgb_sort[0]:
        final[indices[1]] = (((rgb_sort[1] - rgb_sort[0]) * s) / (rgb_sort[2] - rgb_sort[0]))
        final[indices[2]] = s
    else:
        final[indices[1]] = 0
        final[indices[2]] = 0
    final[indices[0]] = 0
    return final


# -----------------------------------------
# Blend modes
# -----------------------------------------
class Blend(metaclass=ABCMeta):
    """Blend base class."""

    @abstractmethod
    def blend(self, coords1: Vector, coords2: Vector) -> Vector:  # pragma: no cover
        """Blend coordinates."""

        raise NotImplementedError('blend is not implemented')


class SeperableBlend(Blend):
    """Blend coordinates."""

    @abstractmethod
    def apply(self, cb: float, cs: float) -> float:  # pragma: no cover
        """Blend two values."""

        raise NotImplementedError('apply is not implemented')

    def blend(self, coords1: Vector, coords2: Vector) -> Vector:
        """Apply blending logic."""

        return [self.apply(cb, cs) for cb, cs in zip(coords1, coords2)]


class NonSeperableBlend(Blend):
    """Non seperable blend method."""

    @abstractmethod
    def apply(self, cb: Vector, cs: Vector) -> Vector:  # pragma: no cover
        """Blend two vectors."""

        raise NotImplementedError('apply is not implemented')

    def blend(self, coords_backgrond: Vector, coords_source: Vector) -> Vector:
        """Apply blending logic."""

        return self.apply(coords_backgrond, coords_source)


class BlendNormal(SeperableBlend):
    """Normal blend mode."""

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        return cs


class BlendMultiply(SeperableBlend):
    """Multiply blend mode."""

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        return cb * cs


class BlendScreen(SeperableBlend):
    """Screen blend mode."""

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        return cb + cs - (cb * cs)


class BlendDarken(SeperableBlend):
    """Darken blend mode."""

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        return min(cb, cs)


class BlendLighten(SeperableBlend):
    """Lighten blend mode."""

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        return max(cb, cs)


class BlendColorDodge(SeperableBlend):
    """Color dodge blend mode."""

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        if cb == 0:
            return 0
        elif cs == 1:
            return 1
        else:
            return min(1, cb / (1 - cs))


class BlendColorBurn(SeperableBlend):
    """Color Burn blend mode."""

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        if cb == 1:
            return 1
        elif cs == 0:
            return 0
        else:
            return 1 - min(1, (1 - cb) / cs)


class BlendOverlay(SeperableBlend):
    """Overlay blend mode."""

    def __init__(self) -> None:
        """Initialize."""

        self.screen = BlendScreen()
        self.multiply = BlendMultiply()

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        if cb >= 0.5:
            return self.screen.apply(cb, 2 * cs - 1)
        else:
            return self.multiply.apply(cb, cs * 2)


class BlendDifference(SeperableBlend):
    """Difference blend mode."""

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        return abs(cb - cs)


class BlendExclusion(SeperableBlend):
    """Exclusion blend mode."""

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        return cb + cs - 2 * cb * cs


class BlendHardLight(SeperableBlend):
    """Hard light blend mode."""

    def __init__(self) -> None:
        """Initialize."""

        self.screen = BlendScreen()
        self.multiply = BlendMultiply()

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        if cs <= 0.5:
            return self.multiply.apply(cb, cs * 2)
        else:
            return self.screen.apply(cb, 2 * cs - 1)


class BlendSoftLight(SeperableBlend):
    """Soft light blend mode."""

    def apply(self, cb: float, cs: float) -> float:
        """Blend two values."""

        if cs <= 0.5:
            return cb - (1 - 2 * cs) * cb * (1 - cb)
        else:
            if cb <= 0.25:
                d = ((16 * cb - 12) * cb + 4) * cb
            else:
                d = math.sqrt(cb)
            return cb + (2 * cs - 1) * (d - cb)


class BlendHue(NonSeperableBlend):
    """Hue blend mode."""

    def apply(self, cb: Vector, cs: Vector) -> Vector:
        """Blend two vectors."""

        return set_lum(set_sat(cs, sat(cb)), lum(cb))


class BlendSaturation(NonSeperableBlend):
    """Saturation blend mode."""

    def apply(self, cb: Vector, cs: Vector) -> Vector:
        """Blend two vectors."""

        return set_lum(set_sat(cb, sat(cs)), lum(cb))


class BlendLuminosity(NonSeperableBlend):
    """Luminosity blend mode."""

    def apply(self, cb: Vector, cs: Vector) -> Vector:
        """Blend two vectors."""
        return set_lum(cb, lum(cs))


class BlendColor(NonSeperableBlend):
    """Color blend mode."""

    def apply(self, cb: Vector, cs: Vector) -> Vector:
        """Blend two vectors."""

        return set_lum(cs, lum(cb))


SUPPORTED = {
    "normal": BlendNormal(),
    "multiply": BlendMultiply(),
    "screen": BlendScreen(),
    "darken": BlendDarken(),
    "lighten": BlendLighten(),
    "color-dodge": BlendColorDodge(),
    "color-burn": BlendColorBurn(),
    "overlay": BlendOverlay(),
    "difference": BlendDifference(),
    "exclusion": BlendExclusion(),
    "hard-light": BlendHardLight(),
    "soft-light": BlendSoftLight(),
    "hue": BlendHue(),
    "saturation": BlendSaturation(),
    "luminosity": BlendLuminosity(),
    "color": BlendColor(),
}  # type: dict[str, Blend]


def get_blender(blend: str) -> Blend:
    """Get desired blend mode."""

    blender = SUPPORTED.get(blend)
    if not blender:
        raise ValueError("'{}' is not a recognized blend mode".format(blend))
    return blender
