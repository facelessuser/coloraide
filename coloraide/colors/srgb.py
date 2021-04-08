"""SRGB color class."""
from ._space import Space
from ._space import RE_DEFAULT_MATCH
from ._gamut import GamutBound
from .xyz import XYZ
from . import _convert as convert
from .. import util
import re
import math


def lin_srgb_to_xyz(rgb):
    """
    Convert an array of linear-light sRGB values to CIE XYZ using sRGB's own white.

    D65 (no chromatic adaptation)
    """

    m = [
        [0.4123907992659593, 0.357584339383878, 0.1804807884018343],
        [0.2126390058715102, 0.715168678767756, 0.0721923153607337],
        [0.0193308187155918, 0.119194779794626, 0.9505321522496608]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_srgb(xyz):
    """Convert XYZ to linear-light sRGB."""

    m = [
        [3.2409699419045226, -1.537383177570094, -0.4986107602930036],
        [-0.9692436362808796, 1.8759675015077202, 0.0415550574071756],
        [0.0556300796969936, -0.2039769588889765, 1.0569715142428784]
    ]

    return util.dot(m, xyz)


def lin_srgb(rgb):
    """
    Convert an array of sRGB values in the range 0.0 - 1.0 to linear light (un-corrected) form.

    https://en.wikipedia.org/wiki/SRGB
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i < 0.04045:
            result.append(i / 12.92)
        else:
            result.append(math.copysign(((abs_i + 0.055) / 1.055) ** 2.4, i))
    return result


def gam_srgb(rgb):
    """
    Convert an array of linear-light sRGB values in the range 0.0-1.0 to gamma corrected form.

    https://en.wikipedia.org/wiki/SRGB
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i > 0.0031308:
            result.append(math.copysign((1.055 * abs_i ** (1 / 2.4) - 0.055), i))
        else:
            result.append(12.92 * i)
    return result


class SRGB(Space):
    """SRGB class."""

    SPACE = "srgb"
    # In addition to the current gamut, check HSL as it is much more sensitive to small
    # gamut changes. This is mainly for a better user experience. Colors will still be
    # mapped/clipped in the current space, unless specified otherwise.
    GAMUT_CHECK = "hsl"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    CHANNEL_NAMES = ("red", "green", "blue", "alpha")
    WHITE = convert.WHITES["D65"]

    _range = (
        GamutBound([0.0, 1.0]),
        GamutBound([0.0, 1.0]),
        GamutBound([0.0, 1.0])
    )

    @property
    def red(self):
        """Adjust red."""

        return self._coords[0]

    @red.setter
    def red(self, value):
        """Adjust red."""

        self._coords[0] = self._handle_input(value)

    @property
    def green(self):
        """Adjust green."""

        return self._coords[1]

    @green.setter
    def green(self, value):
        """Adjust green."""

        self._coords[1] = self._handle_input(value)

    @property
    def blue(self):
        """Adjust blue."""

        return self._coords[2]

    @blue.setter
    def blue(self, value):
        """Adjust blue."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def _to_xyz(cls, rgb):
        """SRGB to XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lin_srgb_to_xyz(lin_srgb(rgb)))

    @classmethod
    def _from_xyz(cls, xyz):
        """XYZ to SRGB."""

        return gam_srgb(xyz_to_lin_srgb(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz)))
