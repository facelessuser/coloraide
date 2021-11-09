"""HSL class."""
from ...spaces import Space, RE_DEFAULT_MATCH, FLG_ANGLE, FLG_OPT_PERCENT, GamutBound, Cylindrical
from ..srgb.base import SRGB
from ... import util
import re
from ...util import Vector, MutableVector
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color


def srgb_to_hsl(rgb: Vector) -> MutableVector:
    """SRGB to HSL."""

    r, g, b = rgb
    mx = max(rgb)
    mn = min(rgb)
    h = util.NaN
    s = 0.0
    l = (mn + mx) / 2
    c = mx - mn

    if c != 0.0:
        if mx == r:
            h = (g - b) / c
        elif mx == g:
            h = (b - r) / c + 2.0
        else:
            h = (r - g) / c + 4.0
        s = 0 if l == 0 or l == 1 else (mx - l) / min(l, 1 - l)
        h *= 60.0
        if s == 0:
            h = util.NaN

    return [util.constrain_hue(h), s, l]


def hsl_to_srgb(hsl: Vector) -> MutableVector:
    """
    HSL to RGB.

    https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB_alternative
    """

    h, s, l = hsl
    h = util.no_nan(h)
    h = h % 360

    def f(n: int) -> float:
        """Calculate the channels."""
        k = (n + h / 30) % 12
        a = s * min(l, 1 - l)
        return l - a * max(-1, min(k - 3, 9 - k, 1))

    return [f(0), f(8), f(4)]


class HSL(Cylindrical, Space):
    """HSL class."""

    SPACE = "hsl"
    SERIALIZE = ("--hsl",)
    CHANNEL_NAMES = ("h", "s", "l", "alpha")
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "lightness": "l"
    }
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"
    GAMUT_CHECK = "srgb"

    BOUNDS = (
        GamutBound(0.0, 360.0, FLG_ANGLE),
        GamutBound(0.0, 1.0, FLG_OPT_PERCENT),
        GamutBound(0.0, 1.0, FLG_OPT_PERCENT)
    )

    @property
    def h(self) -> float:
        """Hue channel."""

        return self._coords[0]

    @h.setter
    def h(self, value: float) -> None:
        """Shift the hue."""

        self._coords[0] = self._handle_input(value)

    @property
    def s(self) -> float:
        """Saturation channel."""

        return self._coords[1]

    @s.setter
    def s(self, value: float) -> None:
        """Saturate or unsaturate the color by the given factor."""

        self._coords[1] = self._handle_input(value)

    @property
    def l(self) -> float:
        """Lightness channel."""

        return self._coords[2]

    @l.setter
    def l(self, value: float) -> None:
        """Set lightness channel."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def null_adjust(cls, coords: MutableVector, alpha: float) -> Tuple[MutableVector, float]:
        """On color update."""

        if coords[1] == 0:
            coords[0] = util.NaN

        return coords, alpha

    @classmethod
    def _to_srgb(cls, parent: 'Color', hsl: Vector) -> MutableVector:
        """To sRGB."""

        return hsl_to_srgb(hsl)

    @classmethod
    def _from_srgb(cls, parent: 'Color', rgb: Vector) -> MutableVector:
        """From sRGB."""

        return srgb_to_hsl(rgb)

    @classmethod
    def _to_xyz(cls, parent: 'Color', hsl: Vector) -> MutableVector:
        """To XYZ."""

        return SRGB._to_xyz(parent, cls._to_srgb(parent, hsl))

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """From XYZ."""

        return cls._from_srgb(parent, SRGB._from_xyz(parent, xyz))
