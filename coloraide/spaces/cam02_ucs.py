"""CAM02 UCS."""
from __future__ import annotations
from .cam02 import xyz_to_cam, cam_to_xyz, CAM02JMh
from .cam16_ucs import cam_jmh_to_cam_ucs, cam_ucs_to_cam_jmh
from .lab import Lab
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT
from ..types import Vector


class CAM02UCS(Lab):
    """CAM02 UCS (Jab) class."""

    BASE = "cam02-jmh"
    NAME = "cam02-ucs"
    SERIALIZE = ("--cam02-ucs",)
    MODEL = 'ucs'
    CHANNELS = (
        Channel("j", 0.0, 100.0),
        Channel("a", -50.0, 50.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -50.0, 50.0, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "lightness": "j"
    }
    WHITE = WHITES['2deg']['D65']
    # Use the same environment as CAM02JMh
    ENV = CAM02JMh.ENV

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "j"

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        m = cam_ucs_to_cam_jmh(coords, self.MODEL)[1]
        return abs(m) < self.achromatic_threshold

    def to_base(self, coords: Vector) -> Vector:
        """To base from UCS."""

        return cam_ucs_to_cam_jmh(coords, self.MODEL)

    def from_base(self, coords: Vector) -> Vector:
        """From base to UCS."""

        # Account for negative colorfulness by reconverting as this can many times corrects the problem
        if coords[1] < 0:
            cam16 = xyz_to_cam(cam_to_xyz(J=coords[0], M=coords[1], h=coords[2], env=self.ENV), env=self.ENV)
            coords = [cam16[0], cam16[5], cam16[2]]

        return cam_jmh_to_cam_ucs(coords, self.MODEL)


class CAM02LCD(CAM02UCS):
    """CAM02 LCD (Jab) class."""

    NAME = "cam02-lcd"
    SERIALIZE = ("--cam02-lcd",)
    MODEL = 'lcd'
    CHANNELS = (
        Channel("j", 0.0, 100.0),
        Channel("a", -70.0, 70.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -70.0, 70.0, flags=FLG_MIRROR_PERCENT)
    )


class CAM02SCD(CAM02UCS):
    """CAM02 SCD (Jab) class."""

    NAME = "cam02-scd"
    SERIALIZE = ("--cam02-scd",)
    MODEL = 'scd'
    CHANNELS = (
        Channel("j", 0.0, 100.0),
        Channel("a", -40.0, 40.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -40.0, 40.0, flags=FLG_MIRROR_PERCENT)
    )
