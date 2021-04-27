"""
Oklab class.

https://bottosson.github.io/posts/oklab/
"""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound
from . import _cat
from .xyz import XYZ
from .. import util
import re

m1 = [
    [0.8189330101, 0.0329845436, 0.0482003018],
    [0.3618667424, 0.9293118715, 0.2643662691],
    [-0.1288597137, 0.0361456387, 0.6338517070]
]

m2 = [
    [0.2104542553, 1.9779984951, 0.0259040371],
    [0.7936177850, -2.4285922050, 0.7827717662],
    [-0.0040720468, 0.4505937099, -0.8086757660]
]

m1i = [
    [1.2270138511035211, -0.0405801784232806, -0.0763812845057069],
    [-0.5577999806518223, 1.11225686961683, -0.4214819784180127],
    [0.2812561489664678, -0.0716766786656012, 1.5861632204407947]
]

m2i = [
    [0.9999999984505199, 1.0000000088817607, 1.0000000546724108],
    [0.3963377921737679, -0.1055613423236564, -0.0894841820949658],
    [0.2158037580607588, -0.0638541747717059, -1.2914855378640917]
]


def xyz_d65_to_oklab(xyzd65):
    """XYZ D65 to Oklab."""

    return util.dot([util.cbrt(x) for x in util.dot(xyzd65, m1)], m2)


def oklab_to_xyz_d65(oklab):
    """From XYZ to LMS."""

    return util.dot([x ** 3 for x in util.dot(oklab, m2i)], m1i)


class Oklab(Space):
    """Oklab class."""

    SPACE = "oklab"
    CHANNEL_NAMES = ("lightness", "a", "b", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = _cat.WHITES["D65"]

    RANGE = (
        GamutUnbound([0, 1]),
        GamutUnbound([-0.5, 0.5]),
        GamutUnbound([-0.5, 0.5])
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
    def _to_xyz(cls, oklab):
        """To XYZ."""

        return _cat.chromatic_adaption(cls.white(), XYZ.white(), oklab_to_xyz_d65(oklab))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return xyz_d65_to_oklab(_cat.chromatic_adaption(XYZ.white(), cls.white(), xyz))
