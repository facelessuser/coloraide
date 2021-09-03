"""LCH class."""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, Cylindrical, Angle, OptionalPercent
from .oklab import Oklab
from .. import util
import re
import math

ACHROMATIC_THRESHOLD = 0.0002


def oklab_to_oklch(oklab):
    """Oklab to Oklch."""

    l, a, b = oklab

    c = math.sqrt(a ** 2 + b ** 2)
    h = math.degrees(math.atan2(b, a))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = util.NaN

    return [l, c, util.constrain_hue(h)]


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
    SERIALIZE = ("--oklch",)
    CHANNEL_NAMES = ("lightness", "chroma", "hue", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    RANGE = (
        GamutUnbound([OptionalPercent(0), OptionalPercent(1)]),
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
    def _to_oklab(cls, parent, oklch):
        """To Lab."""

        return oklch_to_oklab(oklch)

    @classmethod
    def _from_oklab(cls, parent, oklab):
        """To Lab."""

        return oklab_to_oklch(oklab)

    @classmethod
    def _to_xyz(cls, parent, oklch):
        """To XYZ."""

        return Oklab._to_xyz(parent, cls._to_oklab(parent, oklch))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return cls._from_oklab(parent, Oklab._from_xyz(parent, xyz))
