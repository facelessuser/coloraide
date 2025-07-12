"""Color harmonies."""
from __future__ import annotations
import math
from abc import ABCMeta, abstractmethod
from . import algebra as alg
from .spaces import Labish, Luminant, Prism, Space  # noqa: F401
from .spaces.hsl import hsl_to_srgb, srgb_to_hsl
from .cat import WHITES
from . import util
from .types import Vector, AnyColor
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  #pragma: no cover
    from .color import Color

WHITE = util.xy_to_xyz(WHITES['2deg']['D65'])
BLACK = [0, 0, 0]


def adjust_hue(hue: float, deg: float) -> float:
    """Adjust hue by the given degree."""

    return hue + deg


def get_cylinder(color: Color) -> tuple[Vector, int]:
    """Return cylindrical values from a select number of color spaces on the fly."""

    space = color.space()

    if color._space.is_polar():
        return color[:-1], color._space.hue_index()  # type: ignore[attr-defined]

    cs = color.CS_MAP[color.space()]  # type: Space
    achromatic = color.is_achromatic()

    if isinstance(cs, Labish):
        idx = cs.indexes()
        values = color[:-1]
        c, h = alg.rect_to_polar(values[idx[1]], values[idx[2]])
        return [values[idx[0]], c, h if not achromatic else alg.NaN], 2

    if isinstance(cs, Prism) and not isinstance(cs, Luminant):
        coords = color[:-1]
        idx = cs.indexes()
        offset_1 = cs.channels[idx[0]].low
        offset_2 = cs.channels[idx[1]].low
        offset_3 = cs.channels[idx[2]].low

        scale_1 = cs.channels[idx[0]].high
        scale_2 = cs.channels[idx[1]].high
        scale_3 = cs.channels[idx[2]].high
        coords = [coords[i] for i in idx]
        # Scale and offset the values such that channels are between 0 - 1
        coords[0] = (coords[0] - offset_1) / (scale_1 - offset_1)
        coords[1] = (coords[1] - offset_2) / (scale_2 - offset_2)
        coords[2] = (coords[2] - offset_3) / (scale_3 - offset_3)
        hsl = srgb_to_hsl(coords)
        if achromatic:
            hsl[0] = alg.NaN
        return hsl, 0

    raise ValueError(f'Unsupported color space type {space}')  # pragma: no cover


def from_cylinder(color: AnyColor, coords: Vector) -> AnyColor:
    """From a cylinder values, convert back to the original color."""

    space = color.space()
    if color._space.is_polar():
        return color.new(space, coords, color[-1])

    cs = color.CS_MAP[color.space()]  # type: Space

    if isinstance(cs, Labish):
        a, b = alg.polar_to_rect(coords[1], 0 if math.isnan(coords[2]) else coords[2])
        idx = cs.indexes()
        lab = [0.0] * 3
        lab[idx[0]] = coords[0]
        lab[idx[1]] = a
        lab[idx[2]] = b
        return color.new(space, lab, color[-1])

    if isinstance(cs, Prism):
        if math.isnan(coords[0]):
            coords[0] = 0
        coords = hsl_to_srgb(coords)
        idx = cs.indexes()
        offset_1 = cs.channels[idx[0]].low
        offset_2 = cs.channels[idx[1]].low
        offset_3 = cs.channels[idx[2]].low

        scale_1 = cs.channels[idx[0]].high
        scale_2 = cs.channels[idx[1]].high
        scale_3 = cs.channels[idx[2]].high
        # Scale and offset the values back to the origin space's configuration
        coords[0] = coords[0] * (scale_1 - offset_1) + offset_1
        coords[1] = coords[1] * (scale_2 - offset_2) + offset_2
        coords[2] = coords[2] * (scale_3 - offset_3) + offset_3
        ordered = [0.0, 0.0, 0.0]
        # Consistently order a given color spaces points based on its type
        for e, c in enumerate(coords):
            ordered[idx[e]] = c
        return color.new(space, ordered, color[-1])

    raise ValueError(f'Unsupported color space type {space}')  # pragma: no cover


class Harmony(metaclass=ABCMeta):
    """Color harmony."""

    @abstractmethod
    def harmonize(self, color: AnyColor, space: str) -> list[AnyColor]:
        """Get color harmonies."""


class Monochromatic(Harmony):
    """
    Monochromatic harmony.

    Take a given color and create both tints and shades from black -> color -> white.
    With a default count of 5, the goal is to generate 2 shades and 2 tints on either
    side of the seed color, assuming a perfectly centered tone in the middle. If the color
    is closer to black, more tints will be returned than shades and vice versa.

    If an achromatic color is specified as the input, black and white can be returned, otherwise,
    black and white is usually not returned to only return non-achromatic palettes.
    """

    DELTA_E = '2000'

    def harmonize(self, color: AnyColor, space: str, count: int = 5) -> list[AnyColor]:
        """Get color harmonies."""

        if count < 1:
            raise ValueError(f'Cannot generate a monochromatic palette of {count} colors.')

        # Convert color space
        color1 = color.convert(space, norm=False).normalize()

        is_cyl = color1._space.is_polar()

        cs = color1._space
        if not is_cyl and not isinstance(cs, Labish) and not (isinstance(cs, Prism) and not isinstance(cs, Luminant)):
            raise ValueError(f'Unsupported color space type {color.space()}')

        # If only one color is requested, just return the current color.
        if count == 1:
            return [color1]

        # Create black and white so we can generate tints and shades
        # Ensure hue and alpha is masked so we don't interpolate them.
        mask = ['hue', 'alpha'] if is_cyl else ['alpha']
        w = color1.new('xyz-d65', WHITE, math.nan)
        max_lum = w[1]
        w.convert(space, fit=True, in_place=True, norm=False).mask(mask, in_place=True)
        b = color1.new('xyz-d65', BLACK, math.nan)
        min_lum = b[1]
        b.convert(space, fit=True, in_place=True, norm=False).mask(mask, in_place=True)

        # Minimum steps should be adjusted to account for trimming off white and
        # black if the color is not achromatic. Additionally, prepare our slice
        # to remove black and white if required, but always trim duplicate target
        # color from left side.
        if not color1.is_achromatic():
            min_steps = count + 3
            ltrim, rtrim = slice(1, -1, None), slice(None, -1, None)
        else:
            min_steps = count + 1
            ltrim, rtrim = slice(None, -1, None), slice(None, None, None)

        # Calculate how many tints and shades we need to generate
        luminance = color1.luminance()
        if luminance <= min_lum:
            steps_w = min_steps
            steps_b = 0
        elif luminance >= max_lum:
            steps_b = min_steps - 1
            steps_w = 0
        else:
            db = b.delta_e(color1, method=self.DELTA_E)
            dw = w.delta_e(color1, method=self.DELTA_E)
            steps_w = int(alg.round_half_up((dw / (db + dw)) * min_steps))
            steps_b = min_steps - steps_w

        kwargs = {
            'space': space,
            'method': 'linear',
            'out_space': space
        }  # type: dict[str, Any]

        # Very close to black or is black, no need to interpolate from black to current color
        if steps_b <= 1:
            left = []
            if steps_b == 1:
                left.extend(color1.steps([b, color1], steps=steps_b, **kwargs))
            right = color1.steps([color1, w], steps=min(min_steps - (1 + steps_b), steps_w), **kwargs)[rtrim]

        # Very close to white or is white, no need to interpolate from current color to white
        elif steps_w <= 1:
            right = []
            if steps_w == 1:
                right.extend(color1.steps([color1, w], steps=steps_w, **kwargs))
            right.insert(0, color1.clone())
            left = color1.steps([b, color1], steps=min(min_steps - (1 + steps_w), steps_b), **kwargs)[ltrim]

        # Anything else in between
        else:
            left = color1.steps([b, color1], steps=steps_b, **kwargs)[ltrim]
            right = color1.steps([color1, w], steps=steps_w, **kwargs)[rtrim]

        # Extract a subset of the results
        len_l = len(left)
        len_r = len(right)
        l = int(count // 2)
        r = l + (1 if count % 2 else 0)
        if len_r < r:
            return left[-count + len_r:] + right
        elif len_l < l:
            return left + right[:count - len_l]
        return left[-l:] + right[:r]


class Geometric(Harmony):
    """Geometrically space the colors."""

    def __init__(self) -> None:
        """Initialize the count."""

        super().__init__()
        self.count = 12

    def harmonize(self, color: AnyColor, space: str) -> list[AnyColor]:
        """Get color harmonies."""

        # Get the color cylinder
        color = color.convert(space, norm=False).normalize()
        coords, h_idx = get_cylinder(color)

        # Adjusts hue and convert to the final color
        degree = current = 360.0 / self.count
        colors = [from_cylinder(color, coords)]
        for _ in range(self.count - 1):
            coords2 = coords[:]
            coords2[h_idx] = adjust_hue(coords2[h_idx], current)
            colors.append(from_cylinder(color, coords2))
            current += degree
        return colors


class Wheel(Geometric):
    """Generate a color wheel."""

    def harmonize(self, color: AnyColor, space: str, count: int = 12) -> list[AnyColor]:
        """Generate a color wheel with the given count."""

        self.count = count
        return super().harmonize(color, space)


class Complementary(Geometric):
    """Complementary colors."""

    def __init__(self) -> None:
        """Initialize the count."""

        self.count = 2


class Triadic(Geometric):
    """Triadic colors."""

    def __init__(self) -> None:
        """Initialize the count."""

        self.count = 3


class TetradicSquare(Geometric):
    """Tetradic (square)."""

    def __init__(self) -> None:
        """Initialize the count."""

        self.count = 4


class SplitComplementary(Harmony):
    """Split Complementary colors."""

    def harmonize(self, color: AnyColor, space: str) -> list[AnyColor]:
        """Get color harmonies."""

        # Get the color cylinder
        color = color.convert(space, norm=False).normalize()
        coords, h_idx = get_cylinder(color)

        # Adjusts hue and convert to the final color
        colors = [from_cylinder(color, coords)]
        clone = coords[:]
        clone[h_idx] = adjust_hue(clone[h_idx], -210)
        colors.append(from_cylinder(color, clone))
        coords[h_idx] = adjust_hue(coords[h_idx], 210)
        colors.insert(0, from_cylinder(color, coords))
        return colors


class Analogous(Harmony):
    """Analogous colors."""

    def harmonize(self, color: AnyColor, space: str) -> list[AnyColor]:
        """Get color harmonies."""

        # Get the color cylinder
        color = color.convert(space, norm=False).normalize()
        coords, h_idx = get_cylinder(color)

        # Adjusts hue and convert to the final color
        colors = [from_cylinder(color, coords)]
        clone = coords[:]
        clone[h_idx] = adjust_hue(clone[h_idx], 30)
        colors.append(from_cylinder(color, clone))
        coords[h_idx] = adjust_hue(coords[h_idx], -30)
        colors.insert(0, from_cylinder(color, coords))
        return colors


class TetradicRect(Harmony):
    """Tetradic (rectangular) colors."""

    def harmonize(self, color: AnyColor, space: str) -> list[AnyColor]:
        """Get color harmonies."""

        # Get the color cylinder
        color = color.convert(space, norm=False).normalize()
        coords, h_idx = get_cylinder(color)

        # Adjusts hue and convert to the final color
        colors = [from_cylinder(color, coords)]
        clone = coords[:]
        clone[h_idx] = adjust_hue(clone[h_idx], 30)
        colors.append(from_cylinder(color, clone))
        clone = coords[:]
        clone[h_idx] = adjust_hue(clone[h_idx], 180)
        colors.append(from_cylinder(color, clone))
        coords[h_idx] = adjust_hue(coords[h_idx], 210)
        colors.append(from_cylinder(color, coords))
        return colors


SUPPORTED = {
    'complement': Complementary(),
    'split': SplitComplementary(),
    'triad': Triadic(),
    'square': TetradicSquare(),
    'rectangle': TetradicRect(),
    'analogous': Analogous(),
    'mono': Monochromatic(),
    'wheel': Wheel()
}  # type: dict[str, Harmony]


def harmonize(color: AnyColor, name: str, space: str, **kwargs: Any) -> list[AnyColor]:
    """Get specified color harmonies."""

    h = SUPPORTED.get(name)
    if not h:
        raise ValueError(f"The color harmony '{name}' cannot be found")

    return h.harmonize(color, space, **kwargs)
