"""Display-p3 color class."""
from ._space import RE_DEFAULT_MATCH
from .srgb import SRGB, lin_srgb, gam_srgb
from .xyz import XYZ
from . import _convert as convert
from .. import util
import re


def lin_p3_to_xyz(rgb):
    """
    Convert an array of linear-light image-p3 values to CIE XYZ using  D65 (no chromatic adaptation).

    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [4.8657094864821610e-01, 2.6566769316909306e-01, 1.9821728523436244e-01],
        [2.2897456406974875e-01, 6.9173852183650641e-01, 7.9286914093744970e-02],
        [-3.9720755169334868e-17, 4.5113381858902638e-02, 1.0439443689009755e+00]
    ]

    # 0 was computed as -3.972075516933488e-17
    return util.dot(m, rgb)


def xyz_to_lin_p3(xyz):
    """Convert XYZ to linear-light P3."""

    m = [
        [2.4934969119414254, -0.9313836179191239, -0.402710784450717],
        [-0.8294889695615746, 1.7626640603183463, 0.0236246858419436],
        [0.0358458302437845, -0.0761723892680418, 0.9568845240076876]
    ]

    return util.dot(m, xyz)


def lin_p3(rgb):
    """Convert an array of image-p3 RGB values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return lin_srgb(rgb)  # same as sRGB


def gam_p3(rgb):
    """Convert an array of linear-light image-p3 RGB  in the range 0.0-1.0 to gamma corrected form."""

    return gam_srgb(rgb)  # same as sRGB


class DisplayP3(SRGB):
    """Display-p3 class."""

    SPACE = "display-p3"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D65"]

    @classmethod
    def _to_xyz(cls, rgb):
        """To XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lin_p3_to_xyz(lin_p3(rgb)))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return gam_p3(xyz_to_lin_p3(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz)))
