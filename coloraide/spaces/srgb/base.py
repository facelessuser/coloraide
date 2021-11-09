"""SRGB color class."""
from ...spaces import RE_DEFAULT_MATCH, Space, GamutBound, FLG_OPT_PERCENT
from ..xyz import XYZ
from ... import util
from ...util import Vector, MutableVector
import re
import math
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color

RGB_TO_XYZ = [
    [0.4123907992659593, 0.357584339383878, 0.18048078840183432],
    [0.21263900587151024, 0.715168678767756, 0.07219231536073373],
    [0.01933081871559182, 0.11919477979462598, 0.9505321522496608]
]

XYZ_TO_RGB = [
    [3.2409699419045226, -1.537383177570094, -0.49861076029300355],
    [-0.9692436362808796, 1.8759675015077202, 0.04155505740717562],
    [0.055630079696993635, -0.2039769588889765, 1.0569715142428784]
]


def lin_srgb_to_xyz(rgb: Vector) -> MutableVector:
    """
    Convert an array of linear-light sRGB values to CIE XYZ using sRGB's own white.

    D65 (no chromatic adaptation)
    """

    return cast(MutableVector, util.dot(RGB_TO_XYZ, rgb))


def xyz_to_lin_srgb(xyz: Vector) -> MutableVector:
    """Convert XYZ to linear-light sRGB."""

    return cast(MutableVector, util.dot(XYZ_TO_RGB, xyz))


def lin_srgb(rgb: Vector) -> MutableVector:
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


def gam_srgb(rgb: Vector) -> MutableVector:
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
    CHANNEL_NAMES = ("r", "g", "b", "alpha")
    CHANNEL_ALIASES = {
        "red": 'r',
        "green": 'g',
        "blue": 'b'
    }
    WHITE = "D65"

    BOUNDS = (
        GamutBound(0.0, 1.0, FLG_OPT_PERCENT),
        GamutBound(0.0, 1.0, FLG_OPT_PERCENT),
        GamutBound(0.0, 1.0, FLG_OPT_PERCENT)
    )

    @property
    def r(self) -> float:
        """Adjust red."""

        return self._coords[0]

    @r.setter
    def r(self, value: float) -> None:
        """Adjust red."""

        self._coords[0] = self._handle_input(value)

    @property
    def g(self) -> float:
        """Adjust green."""

        return self._coords[1]

    @g.setter
    def g(self, value: float) -> None:
        """Adjust green."""

        self._coords[1] = self._handle_input(value)

    @property
    def b(self) -> float:
        """Adjust blue."""

        return self._coords[2]

    @b.setter
    def b(self, value: float) -> None:
        """Adjust blue."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def _to_xyz(cls, parent: 'Color', rgb: Vector) -> MutableVector:
        """SRGB to XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lin_srgb_to_xyz(lin_srgb(rgb)))

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """XYZ to SRGB."""

        return gam_srgb(xyz_to_lin_srgb(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz)))
