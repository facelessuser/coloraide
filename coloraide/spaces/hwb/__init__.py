"""
HWB class.

http://alvyray.com/Papers/CG/HWB_JGTv208.pdf
"""
from __future__ import annotations
from ...spaces import Space, HWBish
from ... import util
from ...cat import WHITES
from ...channels import Channel, FLG_ANGLE
from ...types import Vector


def hsv_to_hwb(hsv: Vector) -> Vector:
    """HSV to HWB."""

    h, s, v = hsv
    return [util.constrain_hue(h), (1 - s) * v, 1 - v]


def hwb_to_hsv(hwb: Vector) -> Vector:
    """HWB to HSV."""

    h, w, b = hwb
    wb = w + b
    if wb >= 1:
        return [util.constrain_hue(h), 0, w / wb]
    v = 1 - b
    return [util.constrain_hue(h), 1 - w / v if v else 1, v]


class HWB(HWBish, Space):
    """HWB class."""

    BASE = "hsv"
    NAME = "hwb"
    SERIALIZE = ("--hwb",)
    CHANNELS = (
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE),
        Channel("w", 0.0, 1.0, bound=True),
        Channel("b", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "hue": "h",
        "whiteness": "w",
        "blackness": "b"
    }
    GAMUT_CHECK = "srgb"
    WHITE = WHITES['2deg']['D65']

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return (coords[1] + coords[2]) >= (1 - 1e-07)

    def to_base(self, coords: Vector) -> Vector:
        """To HSV from HWB."""

        return hwb_to_hsv(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From HSV to HWB."""

        return hsv_to_hwb(coords)
