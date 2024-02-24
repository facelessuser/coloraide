"""HWB class."""
from __future__ import annotations
from ...spaces import Space, HWBish
from ..hsl import srgb_to_hsl, hsl_to_srgb
from ...cat import WHITES
from ...channels import Channel, FLG_ANGLE
from ...types import Vector


def srgb_to_hwb(srgb: Vector) -> Vector:
    """HWB to sRGB."""

    return [srgb_to_hsl(srgb)[0], min(srgb), 1 - max(srgb)]


def hwb_to_srgb(hwb: Vector) -> Vector:
    """HWB to sRGB."""

    h, w, b = hwb
    wb_sum = w + b
    wb_factor = 1 - w - b
    return [w / wb_sum] * 3 if wb_sum >= 1 else [c * wb_factor + w for c in hsl_to_srgb([h, 1, 0.5])]


class HWB(HWBish, Space):
    """HWB class."""

    BASE = "srgb"
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
        """To sRGB from HWB."""

        return hwb_to_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From sRGB to HWB."""

        return srgb_to_hwb(coords)
