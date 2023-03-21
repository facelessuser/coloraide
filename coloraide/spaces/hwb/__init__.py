"""HWB class."""
from __future__ import annotations
from ...spaces import Space, Cylindrical
from ...cat import WHITES
from ...channels import Channel, FLG_ANGLE, FLG_OPT_PERCENT
from ...types import Vector
import math


def hwb_to_hsv(hwb: Vector) -> Vector:
    """HWB to HSV."""

    h, w, b = hwb

    wb = w + b
    if 1 - wb < 2e-07:
        gray = w / wb
        return [0.0, 0.0, gray]

    v = 1 - b
    s = 0 if v == 0 else 1 - w / v

    return [h, s, v]


def hsv_to_hwb(hsv: Vector) -> Vector:
    """HSV to HWB."""

    h, s, v = hsv
    w = v * (1 - s)
    b = 1 - v
    if 1 - (w + b) < 2e-07:
        h = 0.0
    return [h, w, b]


class HWB(Cylindrical, Space):
    """HWB class."""

    BASE = "hsv"
    NAME = "hwb"
    SERIALIZE = ("--hwb",)
    CHANNELS = (
        Channel("h", 0.0, 360.0, bound=True, flags=FLG_ANGLE),
        Channel("w", 0.0, 1.0, bound=True, flags=FLG_OPT_PERCENT),
        Channel("b", 0.0, 1.0, bound=True, flags=FLG_OPT_PERCENT)
    )
    CHANNEL_ALIASES = {
        "hue": "h",
        "whiteness": "w",
        "blackness": "b"
    }
    GAMUT_CHECK = "srgb"
    WHITE = WHITES['2deg']['D65']

    def is_achromatic(self, undefined: list[bool], coords: Vector) -> bool:
        """Check if color is achromatic."""

        _, wdef, bdef = undefined
        if wdef:
            return (1 - coords[2]) < 1e-7
        if bdef:
            return (1 - coords[1]) < 1e-7
        if 1 - (coords[1] + coords[2]) < 2e-07:
            return True

        v = 1 - coords[2]
        s = 0 if v == 0 else 1 - coords[1] / v
        return abs(s) < 1e-4

    def to_base(self, coords: Vector) -> Vector:
        """To HSV from HWB."""

        return hwb_to_hsv(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From HSV to HWB."""

        return hsv_to_hwb(coords)
