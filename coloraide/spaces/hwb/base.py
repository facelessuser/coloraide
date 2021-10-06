"""HWB class."""
from ...spaces import OptionalPercent, Space, RE_DEFAULT_MATCH, Angle, GamutBound, Cylindrical
from ..srgb.base import SRGB
from ..hsv import HSV
from ... import util
import re


def hwb_to_hsv(hwb):
    """HWB to HSV."""

    h, w, b = hwb

    wb = w + b
    if (wb >= 1):
        gray = w / wb
        return [util.NaN, 0.0, gray]

    v = 1 - b
    s = 0 if v == 0 else 1 - w / v
    return [h, s, v]


def hsv_to_hwb(hsv):
    """HSV to HWB."""

    h, s, v = hsv
    w = v * (1 - s)
    b = 1 - v
    if w + b >= 1:
        h = util.NaN
    return [h, w, b]


class HWB(Cylindrical, Space):
    """HWB class."""

    SPACE = "hwb"
    SERIALIZE = ("--hwb",)
    CHANNEL_NAMES = ("h", "w", "b", "alpha")
    CHANNEL_ALIASES = {
        "hue": "h",
        "whiteness": "w",
        "blackness": "b"
    }
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    GAMUT_CHECK = "srgb"
    WHITE = "D65"

    RANGE = (
        GamutBound([Angle(0.0), Angle(360.0)]),
        GamutBound([OptionalPercent(0.0), OptionalPercent(1.0)]),
        GamutBound([OptionalPercent(0.0), OptionalPercent(1.0)])
    )

    @property
    def h(self):
        """Hue channel."""

        return self._coords[0]

    @h.setter
    def h(self, value):
        """Shift the hue."""

        self._coords[0] = self._handle_input(value)

    @property
    def w(self):
        """Whiteness channel."""

        return self._coords[1]

    @w.setter
    def w(self, value):
        """Set whiteness channel."""

        self._coords[1] = self._handle_input(value)

    @property
    def b(self):
        """Blackness channel."""

        return self._coords[2]

    @b.setter
    def b(self, value):
        """Set blackness channel."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def null_adjust(cls, coords, alpha):
        """On color update."""

        if coords[1] + coords[2] >= 1:
            coords[0] = util.NaN
        return coords, alpha

    @classmethod
    def _to_xyz(cls, parent, hwb):
        """SRGB to XYZ."""

        return SRGB._to_xyz(parent, cls._to_srgb(parent, hwb))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """XYZ to SRGB."""

        return cls._from_srgb(parent, SRGB._from_xyz(parent, xyz))

    @classmethod
    def _to_srgb(cls, parent, hwb):
        """To sRGB."""

        return HSV._to_srgb(parent, cls._to_hsv(parent, hwb))

    @classmethod
    def _from_srgb(cls, parent, srgb):
        """From sRGB."""

        return cls._from_hsv(parent, HSV._from_srgb(parent, srgb))

    @classmethod
    def _to_hsl(cls, parent, hwb):
        """To HSL."""

        return HSV._to_hsl(parent, hwb_to_hsv(hwb))

    @classmethod
    def _from_hsl(cls, parent, hsl):
        """From HSL."""

        return hsv_to_hwb(HSV._from_hsl(parent, hsl))

    @classmethod
    def _to_hsv(cls, parent, hwb):
        """To HSV."""

        return hwb_to_hsv(hwb)

    @classmethod
    def _from_hsv(cls, parent, hsv):
        """From HSV."""

        return hsv_to_hwb(hsv)
