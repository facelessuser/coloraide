"""
CAM16 class (JMh).

https://www.imaging.org/site/PDFS/Papers/2000/PICS-0-81/1611.pdf
https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067
https://doi.org/10.1002/col.22131
"""
from __future__ import annotations
from ..spaces import Space, LChish
from .cam16 import CAM16, cam16_jab_to_cam16_jmh, cam16_jmh_to_cam16_jab, xyz_d65_to_cam16_jab
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from ..util import xy_to_xyz
from ..types import Vector
import math


class CAM16JMh(LChish, Space):
    """CAM16 class (JMh)."""

    BASE = "cam16"
    NAME = "cam16-jmh"
    SERIALIZE = ("--cam16-jmh",)
    CHANNEL_ALIASES = {
        "lightness": "j",
        "colorfulness": 'm',
        "hue": 'h'
    }
    WHITE = WHITES['2deg']['D65']
    # Assuming the same environment as our CAM16 Jab. If we used a different
    # environment (viewing conditions), we'd have to have our BASE set as
    # a Jab that shared those conditions, or resolve directly from XYZ.
    ENV = CAM16.ENV
    ACHROMATIC_HUE = cam16_jab_to_cam16_jmh(xyz_d65_to_cam16_jab(xy_to_xyz(WHITE), env=ENV))[-1]
    CHANNELS = (
        Channel("j", 0.0, 100.0, limit=(0.0, None)),
        Channel("m", 0, 105.0, limit=(0.0, None)),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE, nans=ACHROMATIC_HUE)
    )

    def is_achromatic(self, coords: Vector) -> bool | None:
        """Check if color is achromatic."""

        jdef, mdef = [math.isnan(c) for c in coords[:2]]
        if mdef and jdef:
            return False

        elif jdef:
            return coords[1] < 2e-9

        elif mdef:
            return coords[0] == 0.0

        elif coords[0] < 2e-9:
            return True

        # Chroma is complicated
        return None

    def achromatic_hue(self) -> float:
        """Ideal achromatic hue."""

        return self.ACHROMATIC_HUE

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from CAM16."""

        return cam16_jmh_to_cam16_jab(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16."""

        return cam16_jab_to_cam16_jmh(coords)
