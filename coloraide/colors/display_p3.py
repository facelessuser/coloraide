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
        [0.48663264999999994, 0.26566316250000005, 0.19817418749999988],
        [0.22900359999999997, 0.6917267250000001, 0.07926967499999996],
        [-3.972579210032023e-17, 0.04511261250000005, 1.0437173874999994]
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
