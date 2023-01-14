"""Color harmonies."""
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from . import algebra as alg
from .spaces import Cylindrical
from typing import Optional, cast, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color


class Harmony(metaclass=ABCMeta):
    """Color harmony."""

    @abstractmethod
    def harmonize(self, color: Color, space: Optional[str]) -> list[Color]:
        """Get color harmonies."""


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

    def harmonize(self, color: Color, space: Optional[str]) -> list[Color]:
        """Get color harmonies."""

        if space is None:
            space = color.HARMONY

        orig_space = color.space()
        color0 = color.convert(space).normalize()

        if not isinstance(color0._space, Cylindrical):
            raise ValueError('Color space must be cylindrical')

        # Trim off black and white unless the color is achromatic,
        # But always trim duplicate target color from left side.
        if not color0.is_nan('hue'):
            ltrim, rtrim = slice(1, -1, None), slice(None, -1, None)
        else:
            ltrim, rtrim = slice(None, -1, None), slice(None, None, None)

        # Create black and white so we can generate tints and shades
        # Ensure hue and alpha is masked so we don't interpolate them.
        w = color.new('srgb', [1, 1, 1], alg.NaN).convert(space, in_place=True).mask(['hue', 'alpha'], in_place=True)
        b = color.new('srgb', [0, 0, 0], alg.NaN).convert(space, in_place=True).mask(['hue', 'alpha'], in_place=True)

        # Calculate how many tints and shades we need to generate
        db = b.delta_e(color0, method=self.DELTA_E)
        dw = w.delta_e(color0, method=self.DELTA_E)
        steps_w = int(alg.round_half_up((dw / (db + dw)) * self.RANGE))
        steps_b = self.RANGE - steps_w

        # Very close to black or is black, no need to interpolate from black to current color
        if steps_b <= 1:
            left = []
            if steps_b == 1:
                left.extend(color.steps([b, color], steps=steps_b, space=space, out_space=orig_space, method='linear'))
            steps = min(self.RANGE - (1 + steps_b), steps_w)
            right = color.steps([color0, w], steps=steps, space=space, out_space=orig_space, method='linear')[rtrim]

        # Very close to white or is white, no need to interpolate from current color to white
        elif steps_w <= 1:
            right = []
            if steps_w == 1:
                right.extend(
                    color.steps([color0, w], steps=steps_w, space=space, out_space=orig_space, method='linear')
                )
            steps = min(self.RANGE - (1 + steps_w), steps_b)
            right.insert(0, color.clone())
            left = color.steps([b, color], steps=steps, space=space, out_space=orig_space, method='linear')[ltrim]

        else:
            # Anything else in between
            left = color.steps([b, color], steps=steps_b, space=space, out_space=orig_space, method='linear')[ltrim]
            right = color.steps([color0, w], steps=steps_w, space=space, out_space=orig_space, method='linear')[rtrim]

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

    COUNT = 0

    def harmonize(self, color: Color, space: Optional[str]) -> list[Color]:
        """Get color harmonies."""

        if space is None:
            space = color.HARMONY

        orig_space = color.space()
        color0 = color.convert(space)

        if not isinstance(color0._space, Cylindrical):
            raise ValueError('Color space must be cylindrical')

        name = color0._space.hue_name()

        degree = current = 360 / self.COUNT
        colors = [color]
        for _ in range(self.COUNT - 1):
            colors.append(
                color0.clone().set(
                    name,
                    lambda x: cast(float, x + current)
                ).convert(orig_space, in_place=True)
            )
            current += degree
        return colors


class Complementary(Geometric):
    """Complementary colors."""

    COUNT = 2


class Triadic(Geometric):
    """Triadic colors."""

    COUNT = 3


class TetradicSquare(Geometric):
    """Tetradic (square)."""

    COUNT = 4


class SplitComplementary(Harmony):
    """Split Complementary colors."""

    def harmonize(self, color: Color, space: Optional[str]) -> list[Color]:
        """Get color harmonies."""

        if space is None:
            space = color.HARMONY

        orig_space = color.space()
        color0 = color.convert(space)

        if not isinstance(color0._space, Cylindrical):
            raise ValueError('Color space must be cylindrical')

        name = color0._space.hue_name()

        color2 = color0.clone()
        color3 = color0.clone()
        color2.set(name, lambda x: cast(float, x + 210))
        color3.set(name, lambda x: cast(float, x - 210))
        return [
            color,
            color2.convert(orig_space, in_place=True),
            color3.convert(orig_space, in_place=True)
        ]


class Analogous(Harmony):
    """Analogous colors."""

    def harmonize(self, color: Color, space: Optional[str]) -> list[Color]:
        """Get color harmonies."""

        if space is None:
            space = color.HARMONY

        orig_space = color.space()
        color0 = color.convert(space)

        if not isinstance(color0._space, Cylindrical):
            raise ValueError('Color space must be cylindrical')

        name = color0._space.hue_name()

        color2 = color0.clone()
        color3 = color0.clone()
        color2.set(name, lambda x: cast(float, x + 30))
        color3.set(name, lambda x: cast(float, x - 30))
        return [
            color,
            color2.convert(orig_space, in_place=True),
            color3.convert(orig_space, in_place=True)
        ]


class TetradicRect(Harmony):
    """Tetradic (rectangular) colors."""

    def harmonize(self, color: Color, space: Optional[str]) -> list[Color]:
        """Get color harmonies."""

        if space is None:
            space = color.HARMONY

        orig_space = color.space()
        color0 = color.convert(space)

        if not isinstance(color0._space, Cylindrical):
            raise ValueError('Color space must be cylindrical')

        name = color0._space.hue_name()

        color2 = color0.clone()
        color3 = color0.clone()
        color4 = color0.clone()
        color2.set(name, lambda x: cast(float, x + 30))
        color3.set(name, lambda x: cast(float, x + 180))
        color4.set(name, lambda x: cast(float, x + 210))
        return [
            color,
            color2.convert(orig_space, in_place=True),
            color3.convert(orig_space, in_place=True),
            color4.convert(orig_space, in_place=True)
        ]


SUPPORTED = {
    'complement': Complementary(),
    'split': SplitComplementary(),
    'triad': Triadic(),
    'square': TetradicSquare(),
    'rectangle': TetradicRect(),
    'analogous': Analogous(),
    'mono': Monochromatic()
}  # type: dict[str, Harmony]


def harmonize(color: Color, name: str, space: Optional[str]) -> list[Color]:
    """Get specified color harmonies."""

    try:
        h = SUPPORTED[name]
    except KeyError:
        raise ValueError("The color harmony '{}' cannot be found".format(name))

    return h.harmonize(color, space)
