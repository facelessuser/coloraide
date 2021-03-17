"""SRGB color class."""
from ._space import Space
from ._space import RE_DEFAULT_MATCH
from ._gamut import GamutBound
from .xyz import XYZ
from . import _parse as parse
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
        [0.41239079926595934, 0.357584339383878, 0.1804807884018343],
        [0.21263900587151027, 0.715168678767756, 0.07219231536073371],
        [0.01933081871559182, 0.11919477979462598, 0.9505321522496607]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_srgb(xyz):
    """Convert XYZ to linear-light sRGB."""

    m = [
        [3.2409699419045226, -1.537383177570094, -0.4986107602930034],
        [-0.9692436362808796, 1.8759675015077202, 0.04155505740717559],
        [0.05563007969699366, -0.20397695888897652, 1.0569715142428786]
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
            result.append(math.copysign(math.pow((abs_i + 0.055) / 1.055, 2.4), i))
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
            result.append(math.copysign((1.055 * math.pow(abs_i, 1 / 2.4) - 0.055), i))
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
    DEF_VALUE = "color(srgb 0 0 0 / 1)"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    CHANNEL_NAMES = frozenset(["red", "green", "blue", "alpha"])
    WHITE = convert.WHITES["D65"]

    _range = (
        GamutBound([0.0, 1.0]),
        GamutBound([0.0, 1.0]),
        GamutBound([0.0, 1.0])
    )

    def __init__(self, color=DEF_VALUE):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, Space):
            self.red, self.green, self.blue = color.convert(self.space()).coords()
            self.alpha = color.alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self.red, self.green, self.blue, self.alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self.red = color[0]
            self.green = color[1]
            self.blue = color[2]
            self.alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

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
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if 0 <= channel <= 2:
            return parse.norm_float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:
            raise ValueError("Unexpected channel index of '{}'".format(channel))

    @classmethod
    def _to_xyz(cls, rgb):
        """SRGB to XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lin_srgb_to_xyz(lin_srgb(rgb)))

    @classmethod
    def _from_xyz(cls, xyz):
        """XYZ to SRGB."""

        return gam_srgb(xyz_to_lin_srgb(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz)))
