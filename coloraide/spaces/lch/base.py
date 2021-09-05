"""Lch class."""
from ...spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, Cylindrical, Angle, Percent
from ..lab.base import Lab
from ... import util
import re
import math

ACHROMATIC_THRESHOLD = 0.00000000001


def lab_to_lch(lab):
    """Lab to Lch."""

    l, a, b = lab

    c = math.sqrt(a ** 2 + b ** 2)
    h = math.degrees(math.atan2(b, a))

    # Achromatic colors will often get extremely close, but not quite hit zero.
    # Essentially, we want to discard noise through rounding and such.
    if c < ACHROMATIC_THRESHOLD:
        h = util.NaN

    test = [l, c, util.constrain_hue(h)]
    return test


def lch_to_lab(lch):
    """Lch to Lab."""

    l, c, h = lch
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


class LchBase(Cylindrical, Space):
    """Lch class."""

    CHANNEL_NAMES = ("lightness", "chroma", "hue", "alpha")

    RANGE = (
        # I think chroma, specifically should be clamped.
        # Some libraries don't to prevent rounding issues. We should only get
        # negative chroma via direct user input, but when translating to
        # Lab, this will be corrected.
        GamutUnbound([Percent(0.0), Percent(100.0)]),
        GamutUnbound([0.0, 100.0]),
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


class Lch(LchBase):
    """Lch class."""

    SPACE = "lch"
    SERIALIZE = ("--lch",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D50"

    @classmethod
    def _to_lab(cls, parent, lch):
        """To Lab."""

        return lch_to_lab(lch)

    @classmethod
    def _from_lab(cls, parent, lab):
        """To Lab."""

        return lab_to_lch(lab)

    @classmethod
    def _to_xyz(cls, parent, lch):
        """To XYZ."""

        return Lab._to_xyz(parent, cls._to_lab(parent, lch))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return cls._from_lab(parent, Lab._from_xyz(parent, xyz))
