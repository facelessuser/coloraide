"""HSV class."""
from __future__ import annotations
from ..spaces import Space, Cylindrical
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .. import util
from .. import algebra as alg
from ..types import Vector


def hsv_to_hsl(hsv: Vector) -> Vector:
    """
    HSV to HSL.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    h, s, v = hsv
    l = v * (1.0 - s / 2.0)
    s = 0.0 if l == 0 or abs(1 - l) < 1e-08 else (v - l) / min(l, 1.0 - l)

    if abs(s) < 1e-08:
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

    if abs(s) < 1e-08 or v == 0.0:
        h = alg.NaN

    return [util.constrain_hue(h), s, v]


class HSV(Cylindrical, Space):
    """HSL class."""

    BASE = "hsl"
    NAME = "hsv"
    SERIALIZE = ("--hsv",)
    CHANNELS = (
        Channel("h", 0.0, 360.0, bound=True, flags=FLG_ANGLE),
        Channel("s", 0.0, 1.0, bound=True),
        Channel("v", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "value": "v"
    }
    GAMUT_CHECK = "srgb"
    WHITE = WHITES['2deg']['D65']

    def normalize(self, coords: Vector) -> Vector:
        """On color update."""

        coords = alg.no_nans(coords)
        if abs(coords[1]) < 1e-08 or coords[2] == 0.0:
            coords[0] = alg.NaN

        return coords

    def to_base(self, coords: Vector) -> Vector:
        """To HSL from HSV."""

        return hsv_to_hsl(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From HSL to HSV."""

        return hsl_to_hsv(coords)
