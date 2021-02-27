"""HSV class."""
from ._space import Space, RE_DEFAULT_MATCH
from ._cylindrical import Cylindrical
from ._gamut import GamutBound
from . _range import Angle, Percent
from . import _convert as convert
from . import _parse as parse
from .. import util
import re


class HSV(Cylindrical, Space):
    """HSL class."""

    SPACE = "hsv"
    DEF_BG = "color(hsv 0 0 0 / 1)"
    CHANNEL_NAMES = frozenset(["hue", "saturation", "value", "alpha"])
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))

    _range = (
        GamutBound([Angle(0.0), Angle(360.0)]),
        GamutBound([Percent(0.0), Percent(100.0)]),
        GamutBound([Percent(0.0), Percent(100.0)])
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, Space):
            self.hue, self.saturation, self.value = color.convert(self.space()).coords()
            self.alpha = color.alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self.hue, self.saturation, self.value, self.alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self.hue = color[0]
            self.saturation = color[1]
            self.value = color[2]
            self.alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    def is_hue_null(self):
        """Test if hue is null."""

        h, s, v = self.coords()
        return s < util.ACHROMATIC_THRESHOLD

    @property
    def hue(self):
        """Hue channel."""

        return self._coords[0]

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._coords[0] = self._handle_input(value)

    @property
    def saturation(self):
        """Saturation channel."""

        return self._coords[1]

    @saturation.setter
    def saturation(self, value):
        """Saturate or unsaturate the color by the given factor."""

        self._coords[1] = self._handle_input(value)

    @property
    def value(self):
        """Value channel."""

        return self._coords[2]

    @value.setter
    def value(self, value):
        """Set value channel."""

        self._coords[2] = self._handle_input(value)

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

    def to_string(self, *, alpha=None, precision=util.DEF_PREC, fit=True, **kwargs):
        """To string."""

        return super().to_string(alpha=alpha, precision=precision, fit=fit)

    @classmethod
    def _to_xyz(cls, hsv):
        """To XYZ."""

        return convert.srgb_to_xyz(cls._to_srgb(hsv))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return cls._from_srgb(convert.xyz_to_srgb(xyz))

    @classmethod
    def _to_hsl(cls, hsv):
        """To HSL."""

        return convert.hsv_to_hsl(hsv)

    @classmethod
    def _from_hsl(cls, hsl):
        """From HSL."""

        return convert.hsl_to_hsv(hsl)

    @classmethod
    def _to_srgb(cls, hsv):
        """To sRGB."""

        return convert.hsl_to_srgb(cls._to_hsl(hsv))

    @classmethod
    def _from_srgb(cls, rgb):
        """From sRGB."""

        return cls._from_hsl(convert.srgb_to_hsl(rgb))
