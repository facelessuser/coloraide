"""Color harmonies."""
from __future__ import annotations
import math
from abc import ABCMeta, abstractmethod
from . import algebra as alg
from .spaces import Labish, Regular, Space  # noqa: F401
from .spaces.hsl import HSL
from .spaces.lch import LCh
from .cat import WHITES
from . import util
from .types import Vector
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color

WHITE = util.xy_to_xyz(WHITES['2deg']['D65'])
BLACK = [0, 0, 0]


class _HarmonyLCh(LCh):
    """Special LCh mapping class for harmonies."""

    INDEXES = [0, 1, 2]

    def to_base(self, coords: Vector) -> Vector:
        """Convert to the base."""

        ordered = [0.0, 0.0, 0.0]
        for e, c in enumerate(super().to_base(coords)):
            ordered[self.INDEXES[e]] = c
        return ordered

    def from_base(self, coords: Vector) -> Vector:
        """Convert from the base."""

        return super().from_base([coords[i] for i in self.INDEXES])


class _HarmonyHSL(HSL):
    """Special HSL mapping class for harmonies."""

    INDEXES = [0, 1, 2]

    def to_base(self, coords: Vector) -> Vector:
        """Convert to the base."""

        ordered = [0.0, 0.0, 0.0]
        for e, c in enumerate(super().to_base(coords)):
            ordered[self.INDEXES[e]] = c
        return ordered

    def from_base(self, coords: Vector) -> Vector:
        """Convert from the base."""

        return super().from_base([coords[i] for i in self.INDEXES])


def adjust_hue(hue: float, deg: float) -> float:
    """Adjust hue by the given degree."""

    return hue + deg


class Harmony(metaclass=ABCMeta):
    """Color harmony."""

    @abstractmethod
    def harmonize(self, color: Color, space: str) -> list[Color]:
        """Get color harmonies."""

    def get_cylinder(self, color: Color, space: str) -> Color:
        """Create a cylinder from a select number of color spaces on the fly."""

        color = color.convert(space, norm=False).normalize()

        if color._space.is_polar():
            return color

        custom_space = None  # type: None | type['HarmonyLCh'] | type['HarmonyHSL']

        if isinstance(color._space, Labish):
            cs = color._space  # type: Space
            name = color.space()

            class HarmonyLCh(_HarmonyLCh):
                NAME = '-harmony-cylinder'
                SERIALIZE = ('---harmoncy-cylinder',)
                BASE = name
                WHITE = cs.WHITE
                DYAMIC_RANGE = cs.DYNAMIC_RANGE
                INDEXES = cs.indexes()  # type: ignore[attr-defined]
                ORIG_SPACE = cs

                def is_achromatic(self, coords: Vector) -> bool | None:
                    """Check if space is achromatic."""

                    return self.ORIG_SPACE.is_achromatic(self.to_base(coords))

            custom_space = HarmonyLCh

        if isinstance(color._space, Regular):

            cs = color._space
            name = color.space()

            class HarmonyHSL(_HarmonyHSL, HSL):
                NAME = '-harmony-cylinder'
                SERIALIZE = ('---harmoncy-cylinder',)
                BASE = name
                GAMUT_CHECK = name
                CLIP_SPACE = None
                WHITE = cs.WHITE
                DYAMIC_RANGE = cs.DYNAMIC_RANGE
                INDEXES = cs.indexes() if hasattr(cs, 'indexes') else [0, 1, 2]
                ORIG_SPACE = cs

                def is_achromatic(self, coords: Vector) -> bool | None:
                    """Check if space is achromatic."""

                    return self.ORIG_SPACE.is_achromatic(self.to_base(coords))

            custom_space = HarmonyHSL

        if custom_space is not None:

            class ColorCyl(type(color)):  # type: ignore[misc]
                """Custom color."""

            ColorCyl.register(custom_space())

            return ColorCyl(color).convert('-harmony-cylinder')  # type: ignore[no-any-return]

        raise ValueError(f'Unsupported color space type {color.space()}')


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

    def harmonize(self, color: Color, space: str, count: int = 5) -> list[Color]:
        """Get color harmonies."""

        if count < 1:
            raise ValueError(f'Cannot generate a monochromatic palette of {count} colors.')

        # Convert color space
        color1 = color.convert(space, norm=False).normalize()

        is_cyl = color1._space.is_polar()

        if not is_cyl and not isinstance(color1._space, (Labish, Regular)):
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

        self.count = 12

    def harmonize(self, color: Color, space: str) -> list[Color]:
        """Get color harmonies."""

        # Get the color cylinder
        color1 = self.get_cylinder(color, space)
        output = space
        space = color1.space()

        name = color1._space.hue_name()  # type: ignore[attr-defined]

        degree = current = 360.0 / self.count
        colors = []
        for _ in range(self.count - 1):
            colors.append(
                color1.clone().set(name, lambda x, value=current: adjust_hue(x, value))
            )
            current += degree
        colors.insert(0, color1)

        # Using a dynamic cylinder, convert back to original color space
        if output != space:
            colors = [color.new(c.convert(output, in_place=True)) for c in colors]
        return colors


class Wheel(Geometric):
    """Generate a color wheel."""

    def harmonize(self, color: Color, space: str, count: int = 12) -> list[Color]:
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

    def harmonize(self, color: Color, space: str) -> list[Color]:
        """Get color harmonies."""

        # Get the color cylinder
        color1 = self.get_cylinder(color, space)
        output = space
        space = color1.space()
        name = color1._space.hue_name()  # type: ignore[attr-defined]

        color2 = color1.clone().set(name, lambda x: adjust_hue(x, 210))
        color3 = color1.clone().set(name, lambda x: adjust_hue(x, -210))

        # Using a dynamic cylinder, convert back to original color space
        colors = [color1, color2, color3]
        if output != space:
            colors = [color.new(c.convert(output, in_place=True)) for c in colors]
        return colors


class Analogous(Harmony):
    """Analogous colors."""

    def harmonize(self, color: Color, space: str) -> list[Color]:
        """Get color harmonies."""

        color1 = self.get_cylinder(color, space)
        output = space
        space = color1.space()
        name = color1._space.hue_name()  # type: ignore[attr-defined]

        color2 = color1.clone().set(name, lambda x: adjust_hue(x, 30))
        color3 = color1.clone().set(name, lambda x: adjust_hue(x, -30))

        # Using a dynamic cylinder, convert back to original color space
        colors = [color1, color2, color3]
        if output != space:
            colors = [color.new(c.convert(output, in_place=True)) for c in colors]
        return colors


class TetradicRect(Harmony):
    """Tetradic (rectangular) colors."""

    def harmonize(self, color: Color, space: str) -> list[Color]:
        """Get color harmonies."""

        # Get the color cylinder
        color1 = self.get_cylinder(color, space)
        output = space
        space = color1.space()
        name = color1._space.hue_name()  # type: ignore[attr-defined]

        color2 = color1.clone().set(name, lambda x: adjust_hue(x, 30))
        color3 = color1.clone().set(name, lambda x: adjust_hue(x, 180))
        color4 = color1.clone().set(name, lambda x: adjust_hue(x, 210))

        # Using a dynamic cylinder, convert back to original color space
        colors = [color1, color2, color3, color4]
        if output != space:
            colors = [color.new(c.convert(output, in_place=True)) for c in colors]
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


def harmonize(color: Color, name: str, space: str, **kwargs: Any) -> list[Color]:
    """Get specified color harmonies."""

    h = SUPPORTED.get(name)
    if not h:
        raise ValueError(f"The color harmony '{name}' cannot be found")

    return h.harmonize(color, space, **kwargs)
