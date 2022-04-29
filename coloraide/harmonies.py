"""Color harmonies."""
from . import algebra as alg
from .spaces import Cylindrical
from typing import Optional, Type, Dict, List, cast, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color


class Harmony:
    """Color harmony."""

    @classmethod
    def harmonize(cls, color: 'Color', space: Optional[str]) -> List['Color']:
        """Get color harmonies."""


class Monochromatic(Harmony):
    """Monochromatic harmony."""

    @classmethod
    def harmonize(cls, color: 'Color', space: Optional[str]) -> List['Color']:
        """Get color harmonies."""

        if space is None:
            space = color.HARMONY
        orig_space = color.space()

        # Create black and white so we can generate tints and shades
        w = color.new('color(srgb 1 1 1 / none)').convert(space, in_place=True)
        b = color.new('color(srgb 0 0 0 / none)').convert(space, in_place=True)
        color0 = color.convert(space)

        # Calculate how many tints and shades we need to generate
        db = b.delta_e(color0, method="2000")
        dw = w.delta_e(color0, method="2000")
        total = db + dw
        steps_w = int(alg.round_half_up((dw / total) * 11))
        steps_b = int(alg.round_half_up((db / total) * 11))

        if isinstance(color0._space, Cylindrical):
            w.mask(['hue', 'alpha'], in_place=True)
            b.mask(['hue', 'alpha'], in_place=True)
        else:
            w.mask(['alpha'], in_place=True)
            b.mask(['alpha'], in_place=True)

        # Close to black or is black, no need to interpolate from black to current color
        if db < 5:
            left = []
            right = color0.steps(w, steps=steps_w, space=space, out_space=orig_space)[:]

        # Close to white or is white, no need to interpolate from current color to white
        elif dw < 5:
            left = b.steps(color, steps=steps_b, space=space, out_space=orig_space)[:-1]
            right = [color.clone()]

        # Anything else in between
        else:
            left = b.steps(color, steps=steps_b, space=space, out_space=orig_space)[1:-1]
            right = color0.steps(w, steps=steps_w, space=space, out_space=orig_space)[:-1]

        # Assemble a portion of the results to return
        len_l = len(left)
        len_r = len(right)
        if len_r < 3:
            return left[-5 + len_r:] + right
        elif len_l < 2:
            return left + right[:5 - len_l]
        return left[-2:] + right[:3]


class Geometric(Harmony):
    """Geometrically space the colors."""

    COUNT = 0

    @classmethod
    def harmonize(cls, color: 'Color', space: Optional[str]) -> List['Color']:
        """Get color harmonies."""

        if space is None:
            space = color.HARMONY

        orig_space = color.space()
        color0 = color.convert(space)

        if not isinstance(color0._space, Cylindrical):
            raise ValueError('Color space must be cylindrical')

        name = color0._space.hue_name()

        degree = current = 360 / cls.COUNT
        colors = [color]
        for r in range(cls.COUNT - 1):
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

    @classmethod
    def harmonize(cls, color: 'Color', space: Optional[str]) -> List['Color']:
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

    @classmethod
    def harmonize(cls, color: 'Color', space: Optional[str]) -> List['Color']:
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

    @classmethod
    def harmonize(cls, color: 'Color', space: Optional[str]) -> List['Color']:
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
    'complement': Complementary,
    'split': SplitComplementary,
    'triad': Triadic,
    'square': TetradicSquare,
    'rectangle': TetradicRect,
    'analogous': Analogous,
    'mono': Monochromatic
}  # type: Dict[str, Type[Harmony]]


def harmonize(color: 'Color', name: str, space: Optional[str]) -> List['Color']:
    """Get specified color harmonies."""

    try:
        h = SUPPORTED[name]
    except KeyError:
        raise ValueError("The color harmony '{}' cannot be found".format(name))

    return h.harmonize(color, space)
