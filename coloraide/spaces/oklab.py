"""
Oklab class.

https://bottosson.github.io/posts/oklab/
"""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, OptionalPercent
from .xyz import XYZ
from .. import util
import re

m1 = [
    [0.8189330101, 0.0329845436, 0.0482003018],
    [0.3618667424, 0.9293118715, 0.2643662691],
    [-0.1288597137, 0.0361456387, 0.633851707]
]

m2 = [
    [0.2104542553, 1.9779984951, 0.0259040371],
    [0.793617785, -2.428592205, 0.7827717662],
    [-0.0040720468, 0.4505937099, -0.808675766]
]

m1i = [
    [1.2270138511035211, -0.04058017842328059, -0.07638128450570689],
    [-0.5577999806518223, 1.11225686961683, -0.42148197841801266],
    [0.2812561489664678, -0.0716766786656012, 1.5861632204407947]
]

m2i = [
    [0.9999999984505199, 1.0000000088817607, 1.0000000546724108],
    [0.3963377921737679, -0.10556134232365635, -0.08948418209496575],
    [0.2158037580607588, -0.06385417477170591, -1.2914855378640917]
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
    SERIALIZE = ("--oklab",)
    CHANNEL_NAMES = ("lightness", "a", "b", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    RANGE = (
        GamutUnbound([OptionalPercent(0), OptionalPercent(1)]),
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
    def _to_xyz(cls, parent, oklab):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, oklab_to_xyz_d65(oklab))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return xyz_d65_to_oklab(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz))
