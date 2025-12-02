"""
Msh color space.

Accounts for negative lightness and uses degrees for hue instead of radians.

- https://www.kennethmoreland.com/color-maps/ColorMapsExpanded.pdf
"""
import math
from .lch import LCh
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE, HUE_RAD
from ..types import Vector


def lab_to_msh(lab: Vector) -> Vector:
    """Convert CIE LCh to Msh."""

    l, a, b = lab
    m = math.copysign(math.sqrt(l ** 2 + a ** 2 + b ** 2), l)
    s = math.acos(l / m) if m else 0
    h = math.atan2(b, a)
    return [m, s, h % math.tau]


def msh_to_lab(msh: Vector) -> Vector:
    """Convert Msh to CIE Lab."""

    m, s, h = msh
    abs_m = abs(m)
    l = math.copysign(abs_m * math.cos(s), m)
    a = abs_m * math.sin(s) * math.cos(h)
    b = abs_m * math.sin(s) * math.sin(h)
    return [l, a, b]


class Msh(LCh):
    """Msh color space."""

    BASE = "lab-d65"
    NAME = "msh"
    SERIALIZE = ("--msh",)
    CHANNELS = (
        Channel("m", 0.0, 150.0),
        Channel("s", 0.0, 1.6),
        Channel("h", 0.0, math.tau, flags=FLG_ANGLE, hue=HUE_RAD)
    )
    CHANNEL_ALIASES = {
        "magnitude": "m",
        "saturation": "s",
        "hue": "h"
    }
    WHITE = WHITES['2deg']['D65']

    def normalize(self, coords: Vector) -> Vector:
        """Normalize coordinates."""

        if coords[1] < 0:
            coords[1] *= -1.0
            coords[2] += math.pi
        coords[2] %= math.tau
        return coords

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "m"

    def radial_name(self) -> str:
        """Get radial name."""

        return "s"

    def to_base(self, coords: Vector) -> Vector:
        """To Lab from LCh."""

        return msh_to_lab(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From Lab to LCh."""

        return lab_to_msh(coords)
