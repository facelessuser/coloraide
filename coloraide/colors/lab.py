"""LAB class."""
from ._space import Space, RE_DEFAULT_MATCH
from ._gamut import GamutUnbound
from . _range import Percent
from .xyz import XYZ
from . import _convert as convert
from .. import util
import re

EPSILON3 = 216 / 24389  # `6^3 / 29^3`
EPSILON = 24 / 116
RATIO1 = 16 / 116
RATIO2 = 108 / 841
RATIO3 = 841 / 108


def lab_to_xyz(lab):
    """
    Convert Lab to D50-adapted XYZ.

    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    l, a, b = lab

    # compute `f`, starting with the luminance-related term
    fy = (l + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200

    # compute `xyz`
    xyz = [
        fx ** 3 if fx > EPSILON else (fx - RATIO1) * RATIO2,
        fy ** 3 if fy > EPSILON or l > 8 else (fy - RATIO1) * RATIO2,
        fz ** 3 if fz > EPSILON else (fz - RATIO1) * RATIO2
    ]

    # Compute XYZ by scaling `xyz` by reference `white`
    return util.multiply(xyz, LAB.white())


def xyz_to_lab(xyz):
    """Assuming XYZ is relative to D50, convert to CIE Lab from CIE standard."""

    # compute `xyz`, which is XYZ scaled relative to reference white
    xyz = util.divide(xyz, LAB.white())
    # Compute `fx`, `fy`, and `fz`
    fx, fy, fz = [util.cbrt(i) if i > EPSILON3 else (RATIO3 * i) + RATIO1 for i in xyz]

    return (
        (116.0 * fy) - 16.0,
        500.0 * (fx - fy),
        200.0 * (fy - fz)
    )


class LAB(Space):
    """LAB class."""

    SPACE = "lab"
    CHANNEL_NAMES = ("lightness", "a", "b", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D50"]

    _range = (
        GamutUnbound([Percent(0), Percent(100.0)]),  # Technically we could/should clamp the zero side.
        GamutUnbound([-160, 160]),  # No limit, but we could impose one +/-160?
        GamutUnbound([-160, 160])  # No limit, but we could impose one +/-160?
    )

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
    def _to_xyz(cls, lab):
        """To XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lab_to_xyz(lab))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return xyz_to_lab(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz))
