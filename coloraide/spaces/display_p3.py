"""Display-p3 color class."""
from ..spaces import RE_DEFAULT_MATCH
from .srgb.base import SRGB, lin_srgb, gam_srgb
from .xyz import XYZ
from .. import util
import re


def lin_p3_to_xyz(rgb):
    """
    Convert an array of linear-light image-p3 values to CIE XYZ using  D65 (no chromatic adaptation).

    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [4.8663264999999994e-01, 2.6566316250000005e-01, 1.9817418749999988e-01],
        [2.2900359999999997e-01, 6.9172672500000010e-01, 7.9269674999999956e-02],
        [-3.9725792100320233e-17, 4.5112612500000052e-02, 1.0437173874999994e+00]
    ]

    # 0 was computed as -3.972075516933488e-17
    return util.dot(m, rgb)


def xyz_to_lin_p3(xyz):
    """Convert XYZ to linear-light P3."""

    m = [
        [2.493180755328967, -0.9312655254971399, -0.40265972375888187],
        [-0.8295031158210786, 1.7626941211197922, 0.02362508874173957],
        [0.035853625780071716, -0.07618895478265224, 0.9570926215180221]
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
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE, channels=3))
    WHITE = "D65"

    @classmethod
    def _to_xyz(cls, parent, rgb):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lin_p3_to_xyz(lin_p3(rgb)))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return gam_p3(xyz_to_lin_p3(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz)))
