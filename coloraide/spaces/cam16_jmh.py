"""
CAM16 class (JMh).

https://www.imaging.org/site/PDFS/Papers/2000/PICS-0-81/1611.pdf
https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067
https://doi.org/10.1002/col.22131
"""
from __future__ import annotations
from ..spaces import Space, LChish
from .cam16 import CAM16, cam16_jab_to_cam16_jmh, cam16_jmh_to_cam16_jab
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .. import algebra as alg
from ..types import Vector

ACHROMATIC_HUE = 209.5333344635329


class CAM16JMh(LChish, Space):
    """CAM16 class (JMh)."""

    BASE = "cam16"
    NAME = "cam16-jmh"
    SERIALIZE = ("--cam16-jmh",)
    CHANNELS = (
        Channel("j", 0.0, 100.0, limit=(0.0, None)),
        Channel("m", 0, 105.0, limit=(0.0, None)),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )
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

    def achromatic_hue(self) -> float:
        """Ideal achromatic hue."""

        return ACHROMATIC_HUE

    def no_nans(self, coords: Vector) -> Vector:
        """Return coordinates with no undefined values."""

        if alg.is_nan(coords[2]):
            coords[:2] = alg.no_nans(coords[:2])
            coords[2] = ACHROMATIC_HUE
            return coords
        else:
            return alg.no_nans(coords)

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from CAM16."""

        return cam16_jmh_to_cam16_jab(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16."""

        return cam16_jab_to_cam16_jmh(coords)
