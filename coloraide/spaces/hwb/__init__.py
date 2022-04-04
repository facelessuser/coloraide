"""HWB class."""
from ...spaces import Space, Cylindrical
from ...cat import WHITES
from ...gamut.bounds import GamutBound, FLG_ANGLE, FLG_PERCENT
from ... import algebra as alg
from ...types import Vector
from typing import Tuple


def hwb_to_hsv(hwb: Vector) -> Vector:
    """HWB to HSV."""

    h, w, b = hwb

    wb = w + b
    if (wb >= 1):
        gray = w / wb
        return [alg.NaN, 0.0, gray]

    v = 1 - b
    s = 0 if v == 0 else 1 - w / v
    return [h, s, v]


def hsv_to_hwb(hsv: Vector) -> Vector:
    """HSV to HWB."""

    h, s, v = hsv
    w = v * (1 - s)
    b = 1 - v
    if w + b >= 1:
        h = alg.NaN
    return [h, w, b]


class HWB(Cylindrical, Space):
    """HWB class."""

    BASE = "hsv"
    NAME = "hwb"
    SERIALIZE = ("--hwb",)
    CHANNEL_NAMES = ("h", "w", "b")
    CHANNEL_ALIASES = {
        "hue": "h",
        "whiteness": "w",
        "blackness": "b"
    }
    GAMUT_CHECK = "srgb"
    WHITE = WHITES['2deg']['D65']

    BOUNDS = (
        GamutBound(0.0, 360.0, FLG_ANGLE),
        GamutBound(0.0, 1.0, FLG_PERCENT),
        GamutBound(0.0, 1.0, FLG_PERCENT)
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
    def w(self) -> float:
        """Whiteness channel."""

        return self._coords[1]

    @w.setter
    def w(self, value: float) -> None:
        """Set whiteness channel."""

        self._coords[1] = value

    @property
    def b(self) -> float:
        """Blackness channel."""

        return self._coords[2]

    @b.setter
    def b(self, value: float) -> None:
        """Set blackness channel."""

        self._coords[2] = value

    @classmethod
    def null_adjust(cls, coords: Vector, alpha: float) -> Tuple[Vector, float]:
        """On color update."""

        coords = alg.no_nans(coords)
        if coords[1] + coords[2] >= 1:
            coords[0] = alg.NaN
        return coords, alg.no_nan(alpha)

    @classmethod
    def to_base(cls, coords: Vector) -> Vector:
        """To HSV from HWB."""

        return hwb_to_hsv(coords)

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
        """From HSV to HWB."""

        return hsv_to_hwb(coords)
