"""SRGB color class."""
from ...spaces import RE_DEFAULT_MATCH, Space, GamutBound, OptionalPercent
from ..xyz import XYZ
from ... import util
import re
import math


def lin_srgb_to_xyz(rgb):
    """
    Convert an array of linear-light sRGB values to CIE XYZ using sRGB's own white.

    D65 (no chromatic adaptation)
    """

    m = [
        [0.41245643908969226, 0.357576077643909, 0.18043748326639897],
        [0.21267285140562256, 0.715152155287818, 0.07217499330655959],
        [0.019333895582329303, 0.11919202588130297, 0.950304078536368]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_srgb(xyz):
    """Convert XYZ to linear-light sRGB."""

    m = [
        [3.2404541621141045, -1.5371385127977162, -0.49853140955601605],
        [-0.969266030505187, 1.8760108454466944, 0.04155601753034984],
        [0.05564343095911475, -0.20402591351675384, 1.057225188223179]
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
            result.append(math.copysign(1.055 * (util.nth_root(abs_i, 2.4)) - 0.055, i))
        else:
            result.append(12.92 * i)
    return result


class SRGB(Space):
    """SRGB class."""

    SPACE = "srgb"
    # In addition to the current gamut, check HSL as it is much more sensitive to small
    # gamut changes. This is mainly for a better user experience. Colors will still be
    # mapped/clipped in the current space, unless specified otherwise.
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE, channels=3))
    CHANNEL_NAMES = ("red", "green", "blue", "alpha")
    WHITE = "D65"

    RANGE = (
        GamutBound([OptionalPercent(0.0), OptionalPercent(1.0)]),
        GamutBound([OptionalPercent(0.0), OptionalPercent(1.0)]),
        GamutBound([OptionalPercent(0.0), OptionalPercent(1.0)])
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
    def _to_xyz(cls, parent, rgb):
        """SRGB to XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lin_srgb_to_xyz(lin_srgb(rgb)))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """XYZ to SRGB."""

        return gam_srgb(xyz_to_lin_srgb(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz)))
