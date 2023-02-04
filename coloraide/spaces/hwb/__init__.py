"""HWB class."""
from __future__ import annotations
from ...spaces import Space, Cylindrical
from ...cat import WHITES
from ...channels import Channel, FLG_ANGLE, FLG_PERCENT
from ... import algebra as alg
from ...types import Vector


def hwb_to_hsv(hwb: Vector) -> Vector:
    """HWB to HSV."""

    h, w, b = hwb

    wb = w + b
    if 1 - wb < 2e-08:
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
    if 1 - (w + b) < 2e-08:
        h = alg.NaN
    return [h, w, b]


class HWB(Cylindrical, Space):
    """HWB class."""

    BASE = "hsv"
    NAME = "hwb"
    SERIALIZE = ("--hwb",)
    CHANNELS = (
        Channel("h", 0.0, 360.0, bound=True, flags=FLG_ANGLE),
        Channel("w", 0.0, 1.0, bound=True, flags=FLG_PERCENT),
        Channel("b", 0.0, 1.0, bound=True, flags=FLG_PERCENT)
    )
    CHANNEL_ALIASES = {
        "hue": "h",
        "whiteness": "w",
        "blackness": "b"
    }
    GAMUT_CHECK = "srgb"
    WHITE = WHITES['2deg']['D65']

    def normalize(self, coords: Vector) -> Vector:
        """On color update."""

        coords = alg.no_nans(coords)
        if 1 - (coords[1] + coords[2]) < 2e-08:
            coords[0] = alg.NaN
        return coords

    def to_base(self, coords: Vector) -> Vector:
        """To HSV from HWB."""

        return hwb_to_hsv(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From HSV to HWB."""

        return hsv_to_hwb(coords)
