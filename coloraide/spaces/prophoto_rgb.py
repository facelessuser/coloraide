"""Pro Photo RGB color class."""
from ..spaces import RE_DEFAULT_MATCH
from .srgb.base import SRGB
from .xyz import XYZ
from .. import util
import re

ET = 1 / 512
ET2 = 16 / 512


def lin_prophoto_to_xyz(rgb):
    """
    Convert an array of linear-light prophoto-rgb values to CIE XYZ using  D50.D50.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [7.9767494443060449e-01, 1.3519170147409817e-01, 3.1353354095297416e-02],
        [2.8804023786231026e-01, 7.1187409723579020e-01, 8.5664901899719714e-05],
        [0.0000000000000000e+00, 0.0000000000000000e+00, 8.2521000000000000e-01]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_prophoto(xyz):
    """Convert XYZ to linear-light prophoto-rgb."""

    m = [
        [1.3459433009386652, -0.25560750931676696, -0.05111176587088495],
        [-0.544598869458717, 1.508167317720767, 0.020535141586646915],
        [0.0, 0.0, 1.2118127506937628]
    ]

    return util.dot(m, xyz)


def lin_prophoto(rgb):
    """
    Convert an array of prophoto-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form.

    Transfer curve is gamma 1.8 with a small linear portion.

    https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        if abs(i) < ET2:
            result.append(i / 16.0)
        else:
            result.append(util.npow(i, 1.8))
    return result


def gam_prophoto(rgb):
    """
    Convert an array of linear-light prophoto-rgb  in the range 0.0-1.0 to gamma corrected form.

    Transfer curve is gamma 1.8 with a small linear portion.

    https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        if abs(i) < ET:
            result.append(16.0 * i)
        else:
            result.append(util.nth_root(i, 1.8))
    return result


class ProPhotoRGB(SRGB):
    """Pro Photo RGB class."""

    SPACE = "prophoto-rgb"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE, channels=3))
    WHITE = "D50"

    @classmethod
    def _to_xyz(cls, parent, rgb):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lin_prophoto_to_xyz(lin_prophoto(rgb)))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return gam_prophoto(xyz_to_lin_prophoto(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz)))
