"""Lab class."""
from ...spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, Percent
from ..xyz import XYZ
from ... import util
import re

EPSILON = 216 / 24389  # `6^3 / 29^3`
EPSILON3 = 6 / 29  # Cube root of EPSILON
KAPPA = 24389 / 27
KE = 8  # KAPPA * EPSILON = 8


def lab_to_xyz(lab, white):
    """
    Convert Lab to D50-adapted XYZ.

    http://www.brucelindbloom.com/Eqn_Lab_to_XYZ.html

    While the derivation is different than the specification, the results are the same as Appendix D:
    https://www.cdvplus.cz/file/3-publikace-cie15-2004/
    """

    l, a, b = lab

    # compute `f`, starting with the luminance-related term
    fy = (l + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200

    # compute `xyz`
    xyz = [
        fx ** 3 if fx > EPSILON3 else (116 * fx - 16) / KAPPA,
        fy ** 3 if l > KE else l / KAPPA,
        fz ** 3 if fz > EPSILON3 else (116 * fz - 16) / KAPPA
    ]

    # Compute XYZ by scaling `xyz` by reference `white`
    return util.multiply(xyz, white)


def xyz_to_lab(xyz, white):
    """
    Assuming XYZ is relative to D50, convert to CIE Lab from CIE standard.

    http://www.brucelindbloom.com/Eqn_XYZ_to_Lab.html

    While the derivation is different than the specification, the results are the same:
    https://www.cdvplus.cz/file/3-publikace-cie15-2004/
    """

    # compute `xyz`, which is XYZ scaled relative to reference white
    xyz = util.divide(xyz, white)
    # Compute `fx`, `fy`, and `fz`
    fx, fy, fz = [util.cbrt(i) if i > EPSILON else (KAPPA * i + 16) / 116 for i in xyz]

    return (
        (116.0 * fy) - 16.0,
        500.0 * (fx - fy),
        200.0 * (fy - fz)
    )


class LabBase(Space):
    """Lab class."""

    CHANNEL_NAMES = ("lightness", "a", "b", "alpha")

    RANGE = (
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


class Lab(LabBase):
    """Lab class."""

    SPACE = "lab"
    SERIALIZE = ("--lab",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D50"

    @classmethod
    def _to_xyz(cls, parent, lab):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lab_to_xyz(lab, cls.white()))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return xyz_to_lab(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz), cls.white())
