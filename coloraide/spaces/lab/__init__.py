"""Lab class."""
from ...spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, FLG_PERCENT, Labish
from ... import util
import re
from ...util import Vector, MutableVector
from typing import cast

EPSILON = 216 / 24389  # `6^3 / 29^3`
EPSILON3 = 6 / 29  # Cube root of EPSILON
KAPPA = 24389 / 27
KE = 8  # KAPPA * EPSILON = 8


def lab_to_xyz(lab: MutableVector, white: Vector) -> MutableVector:
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
    return cast(MutableVector, util.multiply(xyz, util.xy_to_xyz(white)))


def xyz_to_lab(xyz: MutableVector, white: Vector) -> MutableVector:
    """
    Assuming XYZ is relative to D50, convert to CIE Lab from CIE standard.

    http://www.brucelindbloom.com/Eqn_XYZ_to_Lab.html

    While the derivation is different than the specification, the results are the same:
    https://www.cdvplus.cz/file/3-publikace-cie15-2004/
    """

    # compute `xyz`, which is XYZ scaled relative to reference white
    xyz = cast(MutableVector, util.divide(xyz, util.xy_to_xyz(white)))
    # Compute `fx`, `fy`, and `fz`
    fx, fy, fz = [util.cbrt(i) if i > EPSILON else (KAPPA * i + 16) / 116 for i in xyz]

    return [
        (116.0 * fy) - 16.0,
        500.0 * (fx - fy),
        200.0 * (fy - fz)
    ]


class Lab(Labish, Space):
    """Lab class."""

    BASE = "xyz-d50"
    NAME = "lab"
    SERIALIZE = ("--lab",)
    CHANNEL_NAMES = ("l", "a", "b")
    CHANNEL_ALIASES = {
        "lightness": "l"
    }
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D50"
    BOUNDS = (
        GamutUnbound(0.0, 100.0, FLG_PERCENT),
        GamutUnbound(-160, 160),
        GamutUnbound(-160, 160)
    )

    @property
    def l(self) -> float:
        """L channel."""

        return self._coords[0]

    @l.setter
    def l(self, value: float) -> None:
        """Get true luminance."""

        self._coords[0] = self._handle_input(value)

    @property
    def a(self) -> float:
        """A channel."""

        return self._coords[1]

    @a.setter
    def a(self, value: float) -> None:
        """A axis."""

        self._coords[1] = self._handle_input(value)

    @property
    def b(self) -> float:
        """B channel."""

        return self._coords[2]

    @b.setter
    def b(self, value: float) -> None:
        """B axis."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def to_base(cls, coords: MutableVector) -> MutableVector:
        """To XYZ D50 from Lab."""

        return lab_to_xyz(coords, cls.white())

    @classmethod
    def from_base(cls, coords: MutableVector) -> MutableVector:
        """From XYZ D50 to Lab."""

        return xyz_to_lab(coords, cls.white())
