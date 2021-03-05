"""SRGB Linear color class."""
from ._space import RE_DEFAULT_MATCH
from .srgb import SRGB, lin_srgb_to_xyz, xyz_to_lin_srgb, lin_srgb, gam_srgb
from .xyz import XYZ
from . import _convert as convert
import re


class SRGB_Linear(SRGB):
    """SRGB linear."""

    SPACE = "srgb-linear"
    DEF_VALUE = "color(srgb-linear 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D65"]

    def __init__(self, color=DEF_VALUE):
        """Initialize."""

        super().__init__(color)

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

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lin_srgb_to_xyz(rgb))

    @classmethod
    def _from_xyz(cls, xyz):
        """XYZ to SRGB Linear."""

        return xyz_to_lin_srgb(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz))
