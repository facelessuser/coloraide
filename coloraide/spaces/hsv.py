"""HSV class."""
from ..spaces import Space, Cylindrical
from ..cat import WHITES
from ..gamut.bounds import GamutBound, FLG_ANGLE
from .. import util
from .. import algebra as alg
from ..types import Vector
from typing import Tuple


def hsv_to_hsl(hsv: Vector) -> Vector:
    """
    HSV to HSL.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    h, s, v = hsv
    l = v * (1.0 - s / 2.0)
    s = 0.0 if (l == 0.0 or l == 1.0) else (v - l) / min(l, 1.0 - l)

    if s == 0:
        h = alg.NaN

    return [util.constrain_hue(h), s, l]


def hsl_to_hsv(hsl: Vector) -> Vector:
    """
    HSL to HSV.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    h, s, l = hsl

    v = l + s * min(l, 1.0 - l)
    s = 0.0 if (v == 0.0) else 2 * (1.0 - l / v)

    if s == 0:
        h = alg.NaN

    return [util.constrain_hue(h), s, v]


class HSV(Cylindrical, Space):
    """HSL class."""

    BASE = "hsl"
    NAME = "hsv"
    SERIALIZE = ("--hsv",)
    CHANNEL_NAMES = ("h", "s", "v")
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "value": "v"
    }
    GAMUT_CHECK = "srgb"
    WHITE = WHITES['2deg']['D65']

    BOUNDS = (
        GamutBound(0.0, 360.0, FLG_ANGLE),
        GamutBound(0.0, 1.0),
        GamutBound(0.0, 1.0)
    )

    @property
    def h(self) -> float:
        """Hue channel."""

        return self._coords[0]

    @h.setter
    def h(self, value: float) -> None:
        """Shift the hue."""

        self._coords[0] = value

    @property
    def s(self) -> float:
        """Saturation channel."""

        return self._coords[1]

    @s.setter
    def s(self, value: float) -> None:
        """Saturate or unsaturate the color by the given factor."""

        self._coords[1] = value

    @property
    def v(self) -> float:
        """Value channel."""

        return self._coords[2]

    @v.setter
    def v(self, value: float) -> None:
        """Set value channel."""

        self._coords[2] = value

    @classmethod
    def null_adjust(cls, coords: Vector, alpha: float) -> Tuple[Vector, float]:
        """On color update."""

        coords = alg.no_nans(coords)
        if coords[1] == 0:
            coords[0] = alg.NaN

        return coords, alg.no_nan(alpha)

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To HSL from HSV."""

        return hsv_to_hsl(coords)

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From HSL to HSV."""

        return hsl_to_hsv(coords)
