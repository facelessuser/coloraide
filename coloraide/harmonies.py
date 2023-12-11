"""Color harmonies."""
from __future__ import annotations
import math
from abc import ABCMeta, abstractmethod
from . import algebra as alg
from .spaces import Cylindrical, Labish, Regular, Space  # noqa: F401
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

        if isinstance(color._space, Cylindrical):
            return color

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

            class ColorCyl(type(color)):  # type: ignore[misc]
                """Custom color."""

            ColorCyl.register(HarmonyLCh())

            return ColorCyl(color).convert('-harmony-cylinder')  # type: ignore[no-any-return]

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

            class ColorCyl(type(color)):  # type: ignore[no-redef, misc]
                """Custom color."""

            ColorCyl.register(HarmonyHSL())

            return ColorCyl(color).convert('-harmony-cylinder')  # type: ignore[no-any-return]

        raise ValueError('Unsupported color space type {}'.format(color.space()))


class Monochromatic(Harmony):
    """
    Monochromatic harmony.

    Take a given color and create both tints and shades such that we have `RANGE` total steps ranging
    from black -> color -> white. Normally, we will throw away pure black, pure white, and the duplicate
    target color (as we interpolate with it on both sides) leaving us with RANGE - 3 colors to extract
    the target `STEPS` from. The one exception is when targeting an achromatic color, and in that case,
    we only throw away the duplicate color (though if a color is close enough to white or black, white
    or black may not be included simply because we cannot get a reasonable step that includes it).

    Once we have our `RANGE`, we can extract a total of `STEPS` colors with the target color at the center
    (when possible). If the target color is too close to the either the minimum or maximum color step,
    there may not be enough tints or shades on one side, so the result may have to draw heavier on the
    side that has more plentiful tints or shades which would cause the target color to shift from the center.

    The current `RANGE` was chosen as 12 as it seems to to provide OK contrast in most cases for the monochromatic
    colors. The one exception is with a target color of black or very near black which may return at least one color
    with very low contrast to black. Generally, extremely dark colors do not make a good target for color harmonies,
    but it should be noted that OkLCh's lightness tends to the more darker side. The poor contrast may be
    less with other color spaces.
    """

    DELTA_E = '2000'
    RANGE = 12
    STEPS = 5

    def harmonize(self, color: Color, space: str) -> list[Color]:
        """Get color harmonies."""

        # Convert color space
        color1 = color.convert(space, norm=False).normalize()

        is_cyl = isinstance(color1._space, Cylindrical)

        if not is_cyl and not isinstance(color1._space, (Labish, Regular)):
            raise ValueError('Unsupported color space type {}'.format(color.space()))

        # Trim off black and white unless the color is achromatic,
        # But always trim duplicate target color from left side.
        if not color1.is_achromatic():
            ltrim, rtrim = slice(1, -1, None), slice(None, -1, None)
        else:
            ltrim, rtrim = slice(None, -1, None), slice(None, None, None)

        # Create black and white so we can generate tints and shades
        # Ensure hue and alpha is masked so we don't interpolate them.
        mask = ['hue', 'alpha'] if is_cyl else ['alpha']
        w = color1.new('xyz-d65', WHITE, math.nan)
        w.convert(space, fit=True, in_place=True, norm=False).mask(mask, in_place=True)
        b = color1.new('xyz-d65', BLACK, math.nan)
        b.convert(space, fit=True, in_place=True, norm=False).mask(mask, in_place=True)

        # Calculate how many tints and shades we need to generate
        db = b.delta_e(color1, method=self.DELTA_E)
        dw = w.delta_e(color1, method=self.DELTA_E)
        steps_w = int(alg.round_half_up((dw / (db + dw)) * self.RANGE))
        steps_b = self.RANGE - steps_w

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
            steps = min(self.RANGE - (1 + steps_b), steps_w)
            right = color1.steps([color1, w], steps=steps, **kwargs)[rtrim]

        # Very close to white or is white, no need to interpolate from current color to white
        elif steps_w <= 1:
            right = []
            if steps_w == 1:
                right.extend(color1.steps([color1, w], steps=steps_w, **kwargs))
            steps = min(self.RANGE - (1 + steps_w), steps_b)
            right.insert(0, color1.clone())
            left = color1.steps([b, color1], steps=steps, **kwargs)[ltrim]

        # Anything else in between
        else:
            left = color1.steps([b, color1], steps=steps_b, **kwargs)[ltrim]
            right = color1.steps([color1, w], steps=steps_w, **kwargs)[rtrim]

        # Extract a subset of the results
        len_l = len(left)
        len_r = len(right)
        l = int(self.STEPS // 2)
        r = l + (1 if self.STEPS % 2 else 0)
        if len_r < r:
            return left[-self.STEPS + len_r:] + right
        elif len_l < l:
            return left + right[:self.STEPS - len_l]
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
        raise ValueError("The color harmony '{}' cannot be found".format(name))

    return h.harmonize(color, space, **kwargs)
