"""LAB class."""
from ._space import Space, RE_DEFAULT_MATCH
from ._gamut import GamutUnbound
from . _range import Percent
from . import _parse as parse
from . import _convert as convert
from .. import util
import re
import math

KAPPA = 24389 / 27  # `29^3 / 3^3`
EPSILON = 216 / 24389  # `6^3 / 29^3`


def lab_to_xyz(lab):
    """
    Convert Lab to D50-adapted XYZ.

    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    l, a, b = lab

    # compute `f`, starting with the luminance-related term
    f1 = (l + 16) / 116
    f0 = a / 500 + f1
    f2 = f1 - b / 200

    # compute `xyz`
    xyz = [
        math.pow(f0, 3) if math.pow(f0, 3) > EPSILON else (116 * f0 - 16) / KAPPA,
        math.pow((l + 16) / 116, 3) if l > KAPPA * EPSILON else l / KAPPA,
        math.pow(f2, 3) if math.pow(f2, 3) > EPSILON else (116 * f2 - 16) / KAPPA
    ]

    # Compute XYZ by scaling `xyz` by reference `white`
    return util.multiply(xyz, LAB.white())


def xyz_to_lab(xyz):
    """Assuming XYZ is relative to D50, convert to CIE Lab from CIE standard."""

    # compute `xyz`, which is XYZ scaled relative to reference white
    xyz = util.divide(xyz, LAB.white())
    # Compute `f`
    f = [util.cbrt(i) if i > EPSILON else (KAPPA * i + 16.0) / 116.0 for i in xyz]

    return (
        (116.0 * f[1]) - 16.0,
        500.0 * (f[0] - f[1]),
        200.0 * (f[1] - f[2])
    )


class LAB(Space):
    """LAB class."""

    SPACE = "lab"
    DEF_VALUE = "color(lab 0 0 0 / 1)"
    CHANNEL_NAMES = frozenset(["lightness", "a", "b", "alpha"])
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D50"]

    _range = (
        GamutUnbound([Percent(0), Percent(100.0)]),  # Technically we could/should clamp the zero side.
        GamutUnbound([-160, 160]),  # No limit, but we could impose one +/-160?
        GamutUnbound([-160, 160])  # No limit, but we could impose one +/-160?
    )

    def __init__(self, color=DEF_VALUE):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, Space):
            self.lightness, self.a, self.b = color.convert(self.space()).coords()
            self.alpha = color.alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self.lightness, self.a, self.b, self.alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self.lightness = color[0]
            self.a = color[1]
            self.b = color[2]
            self.alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    @property
    def lightness(self):
        """L channel."""

        return self._coords[0]

    @lightness.setter
    def lightness(self, value):
        """Get true luminance."""

        self._coords[0] = self._handle_input(value)

    @property
    def a(self):
        """A channel."""

        return self._coords[1]

    @a.setter
    def a(self, value):
        """A axis."""

        self._coords[1] = self._handle_input(value)

    @property
    def b(self):
        """B channel."""

        return self._coords[2]

    @b.setter
    def b(self, value):
        """B axis."""

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
    def _to_xyz(cls, lab):
        """To XYZ."""

        return lab_to_xyz(lab)

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return xyz_to_lab(xyz)
