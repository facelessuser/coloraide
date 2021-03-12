"""LCH class."""
from ._space import Space, RE_DEFAULT_MATCH
from .lab import LAB
from ._cylindrical import Cylindrical
from ._gamut import GamutUnbound
from . _range import Angle, Percent
from . import _parse as parse
from . import _convert as convert
from .. import util
import re
import math

ACHROMATIC_THRESHOLD = 0.02


def lab_to_lch(lab):
    """LAB to LCH."""

    l, a, b = lab

    c = math.sqrt(math.pow(a, 2) + math.pow(b, 2))
    h = math.atan2(b, a) * 180 / math.pi

    # This is not actually part of the conversion, but is a fix-up
    # for conversion getting a bit chaotic in regards to hue when
    # chroma approaches zero. This fix-up is intended to make at
    # least colors in the sRGB range a bit more stable with conversion
    # and yield a hue of zero. This minimally affects the overall output.
    # If a 100% accurate result is desired, then we'd want to avoid doing this.
    if c < ACHROMATIC_THRESHOLD:
        h = util.NaN

    test = [l, c, LCH._constrain_hue(h)]
    return test


def lch_to_lab(lch):
    """LCH to LAB."""

    l, c, h = lch
    h = util.no_nan(h)

    # If, for whatever reason (mainly direct user input),
    # if chroma is less than zero, clamp to zero.
    if c < 0.0:
        c = 0.0

    return (
        l,
        c * math.cos(h * math.pi / 180.0),
        c * math.sin(h * math.pi / 180.0)
    )


class LCH(Cylindrical, Space):
    """LCH class."""

    SPACE = "lch"
    DEF_VALUE = "color(lch 0 0 0 / 1)"
    CHANNEL_NAMES = frozenset(["lightness", "chroma", "hue", "alpha"])
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D50"]

    _range = (
        # I think chroma, specifically should be clamped.
        # Some libraries don't to prevent rounding issues. We should only get
        # negative chroma via direct user input, but when translating to
        # Lab, this will be corrected.
        GamutUnbound([Percent(0.0), Percent(100.0)]),
        GamutUnbound([0.0, 100.0]),
        GamutUnbound([Angle(0.0), Angle(360.0)]),
    )

    def __init__(self, color=DEF_VALUE):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, Space):
            self.lightness, self.chroma, self.hue = color.convert(self.space()).coords()
            self.alpha = color.alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self.lightness, self.chroma, self.hue, self.alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self.lightness = color[0]
            self.chroma = color[1]
            self.hue = color[2]
            self.alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    def hue_index(self):
        """Get hue index."""

        return 2

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
    def null_adjust(cls, coords):
        """On color update."""

        if coords[1] < ACHROMATIC_THRESHOLD:
            coords[2] = util.NaN
        return coords

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel in (0, 1):
            return parse.norm_float(value)
        elif channel == 2:
            return parse.norm_deg_channel(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:
            raise ValueError("Unexpected channel index of '{}'".format(channel))

    @classmethod
    def _to_lab(cls, lch):
        """To Lab."""

        return lch_to_lab(lch)

    @classmethod
    def _from_lab(cls, lab):
        """To Lab."""

        return lab_to_lch(lab)

    @classmethod
    def _to_xyz(cls, lch):
        """To XYZ."""

        return LAB._to_xyz(cls._to_lab(lch))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return cls._from_lab(LAB._from_xyz(xyz))
