"""HWB class."""
from ._space import Space, RE_DEFAULT_MATCH
from .srgb import SRGB
from .hsl import HSL
from .hsv import HSV
from ._cylindrical import Cylindrical
from ._gamut import GamutBound
from . _range import Angle, Percent
from . import _parse as parse
from . import _convert as convert
from .. import util
import re


def srgb_to_hwb(rgb):
    """SRGB to HWB."""

    h, s, v = HSV._from_srgb(rgb)
    w = v * (100.0 - s) / 100.0
    b = 100.0 - v
    return HWB._constrain_hue(h), w, b


def hwb_to_srgb(hwb):
    """HWB to RGB."""

    h, w, b = hwb
    w /= 100.0
    b /= 100.0
    wb = w + b

    if wb > 1.0:
        return [w / wb] * 3

    return [(c * (1.0 - w - b)) + w for c in HSL._to_srgb([h, 100.0, 50.0])]


class HWB(Cylindrical, Space):
    """HWB class."""

    SPACE = "hwb"
    DEF_VALUE = "color(hwb 0 0 0 / 1)"
    CHANNEL_NAMES = frozenset(["hue", "blackness", "whiteness", "alpha"])
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    GAMUT_CHECK = "hsl"
    WHITE = convert.WHITES["D65"]

    _range = (
        GamutBound([Angle(0.0), Angle(360.0)]),
        GamutBound([Percent(0.0), Percent(100.0)]),
        GamutBound([Percent(0.0), Percent(100.0)])
    )

    def __init__(self, color=DEF_VALUE):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, Space):
            self.hue, self.whiteness, self.blackness = color.convert(self.space()).coords()
            self.alpha = color.alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self.hue, self.whiteness, self.blackness, self.alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self.hue = color[0]
            self.whiteness = color[1]
            self.blackness = color[2]
            self.alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    @property
    def hue(self):
        """Hue channel."""

        return self._coords[0]

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._coords[0] = self._handle_input(value)

    @property
    def whiteness(self):
        """Whiteness channel."""

        return self._coords[1]

    @whiteness.setter
    def whiteness(self, value):
        """Set whiteness channel."""

        self._coords[1] = self._handle_input(value)

    @property
    def blackness(self):
        """Blackness channel."""

        return self._coords[2]

    @blackness.setter
    def blackness(self, value):
        """Set blackness channel."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def null_adjust(cls, coords):
        """On color update."""

        if coords[1] + coords[2] >= 100:
            coords[0] = util.NaN
        return coords

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel == 0:
            return parse.norm_deg_channel(value)
        elif channel in (1, 2):
            return parse.norm_float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:
            raise ValueError("Unexpected channel index of '{}'".format(channel))

    @classmethod
    def _to_xyz(cls, hwb):
        """SRGB to XYZ."""

        return SRGB._to_xyz(cls._to_srgb(hwb))

    @classmethod
    def _from_xyz(cls, xyz):
        """XYZ to SRGB."""

        return cls._from_srgb(SRGB._from_xyz(xyz))

    @classmethod
    def _to_srgb(cls, hwb):
        """To sRGB."""

        return hwb_to_srgb(hwb)

    @classmethod
    def _from_srgb(cls, srgb):
        """From sRGB."""

        return srgb_to_hwb(srgb)

    @classmethod
    def _to_hsl(cls, hwb):
        """To HSL."""

        return HSL._from_srgb(cls._to_srgb(hwb))

    @classmethod
    def _from_hsl(cls, hsl):
        """From HSL."""

        return cls._from_srgb(HSL._to_srgb(hsl))

    @classmethod
    def _to_hsv(cls, hwb):
        """To HSV."""

        return HSV._from_srgb(cls._to_srgb(hwb))

    @classmethod
    def _from_hsv(cls, hsv):
        """From HSV."""

        return cls._from_srgb(HSV._to_srgb(hsv))
