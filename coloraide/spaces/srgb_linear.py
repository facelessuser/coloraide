"""SRGB Linear color class."""
from ..spaces import RE_DEFAULT_MATCH
from . import _cat
from .srgb import SRGB, lin_srgb_to_xyz, xyz_to_lin_srgb, lin_srgb, gam_srgb
from .xyz import XYZ
import re


class SRGBLinear(SRGB):
    """SRGB linear."""

    SPACE = "srgb-linear"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = _cat.WHITES["D65"]

    @classmethod
    def _to_srgb(cls, rgb):
        """Linear sRGB to sRGB."""

        return gam_srgb(rgb)

    @classmethod
    def _from_srgb(cls, rgb):
        """sRGB to linear sRGB."""

        return lin_srgb(rgb)

    @classmethod
    def _to_xyz(cls, rgb):
        """SRGB Linear to XYZ."""

        return _cat.chromatic_adaption(cls.white(), XYZ.white(), lin_srgb_to_xyz(rgb))

    @classmethod
    def _from_xyz(cls, xyz):
        """XYZ to SRGB Linear."""

        return xyz_to_lin_srgb(_cat.chromatic_adaption(XYZ.white(), cls.white(), xyz))
