"""LCH class."""
from ._space import Space, RE_DEFAULT_MATCH
from .oklab import Oklab
from ._cylindrical import Cylindrical
from ._gamut import GamutUnbound
from . _range import Angle
from . import _convert as convert
from .. import util
import re
import math

ACHROMATIC_THRESHOLD = 0.00000000001


def oklab_to_oklch(oklab):
    """Oklab to Oklch."""

    l, a, b = oklab

    c = math.sqrt(a ** 2 + b ** 2)
    h = math.degrees(math.atan2(b, a))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = util.NaN

    return [l, c, Oklch._constrain_hue(h)]


def oklch_to_oklab(oklch):
    """Oklch to Oklab."""

    l, c, h = oklch
    h = util.no_nan(h)

    # If, for whatever reason (mainly direct user input),
    # if chroma is less than zero, clamp to zero.
    if c < 0.0:
        c = 0.0

    return (
        l,
        c * math.cos(math.radians(h)),
        c * math.sin(math.radians(h))
    )


class Oklch(Cylindrical, Space):
    """Oklch class."""

    SPACE = "oklch"
    CHANNEL_NAMES = ("lightness", "chroma", "hue", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D65"]

    _range = (
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([Angle(0.0), Angle(360.0)]),
    )

    @property
    def lightness(self):
        """Lightness."""

        return self._coords[0]

    @lightness.setter
    def lightness(self, value):
        """Get true luminance."""

        self._coords[0] = self._handle_input(value)

    @property
    def chroma(self):
        """Chroma."""

        return self._coords[1]

    @chroma.setter
    def chroma(self, value):
        """chroma."""

        self._coords[1] = self._handle_input(value)

    @property
    def hue(self):
        """Hue."""

        return self._coords[2]

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def null_adjust(cls, coords, alpha):
        """On color update."""

        if coords[1] < ACHROMATIC_THRESHOLD:
            coords[2] = util.NaN
        return coords, alpha

    @classmethod
    def _to_oklab(cls, oklch):
        """To Lab."""

        return oklch_to_oklab(oklch)

    @classmethod
    def _from_oklab(cls, oklab):
        """To Lab."""

        return oklab_to_oklch(oklab)

    @classmethod
    def _to_xyz(cls, oklch):
        """To XYZ."""

        return Oklab._to_xyz(cls._to_oklab(oklch))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return cls._from_oklab(Oklab._from_xyz(xyz))
