"""SRGB color class."""
import re
from .base import _Color
from .tools import _ColorTools
from .. import util
from ..util import parse
from ..util import convert


class _SRGB(_ColorTools, _Color):
    """SRGB class."""

    SPACE = "srgb"
    DEF_BG = "color(srgb 0 0 0 / 1)"
    _MATCH = re.compile(
        r"(?xi)color\(\s*srgb\s+((?:{float}{sep}){{2}}{float}(?:{asep}{float})?)\s*\)".format(**parse.COLOR_PARTS)
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)
        self._c4 = 0.0

        if isinstance(color, _Color):
            self._cr, self._cg, self._cb = convert.convert(color.coords(), color.space(), self.space())
            self._alpha = color._alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._cr, self._cg, self._cb, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._cr = color[0]
            self._cg = color[1]
            self._cb = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))
        self._update_hue()

    def _update_hue(self):
        """Update hue."""

        if not self.is_achromatic():
            h = convert.srgb_to_hsv(self._cr, self._cg, self._cb)[0]
            self._c4 = h if 0.0 <= h <= 360.0 else h % 360.0

    def mutate(self, obj):
        """Update from color."""

        if self is obj:
            self._update_hue()
            return

        if not isinstance(obj, type(self)):
            obj = self.new(obj)

        self._c1 = obj._c1
        self._c2 = obj._c2
        self._c3 = obj._c3
        self._alpha = obj._alpha
        self._update_hue()

    @property
    def _cr(self):
        """Red channel."""

        return self._c1

    @_cr.setter
    def _cr(self, value):
        """Set red channel."""

        self._c1 = util.clamp(value, 0.0, 1.0)

    @property
    def _cg(self):
        """Green channel."""

        return self._c2

    @_cg.setter
    def _cg(self, value):
        """Set green channel."""

        self._c2 = util.clamp(value, 0.0, 1.0)

    @property
    def _cb(self):
        """Blue channel."""

        return self._c3

    @_cb.setter
    def _cb(self, value):
        """Set blue channel."""

        self._c3 = util.clamp(value, 0.0, 1.0)

    @property
    def _ch(self):
        """Hue channel."""

        return self._c4

    @_ch.setter
    def _ch(self, value):
        """Set hue channel."""

        self._c4 = value if 0.0 <= value <= 360.0 else value % 360.0

    def __str__(self):
        """String."""

        return self.to_string(alpha=True)

    def _grayscale(self):
        """Convert to grayscale."""

        self._cr = self.luminance()
        self._cg = self.luminance()
        self._cb = self.luminance()

    def _mix(self, coords1, coords2, factor, factor2=1.0):
        """Blend the color with the given color."""

        self._cr = self._mix_channel(coords1[0], coords2[0], factor, factor2)
        self._cg = self._mix_channel(coords1[1], coords2[1], factor, factor2)
        self._cb = self._mix_channel(coords1[2], coords2[2], factor, factor2)
        self._update_hue()

    @property
    def red(self):
        """Adjust red."""

        return self._cr

    @red.setter
    def red(self, value):
        """Adjust red."""

        self._cr = self.tx_channel(0, value) if isinstance(value, str) else float(value)
        self._update_hue()

    @property
    def green(self):
        """Adjust green."""

        return self._cg

    @green.setter
    def green(self, value):
        """Adjust green."""

        self._cg = self.tx_channel(1, value) if isinstance(value, str) else float(value)
        self._update_hue()

    @property
    def blue(self):
        """Adjust blue."""

        return self._cb

    @blue.setter
    def blue(self, value):
        """Adjust blue."""

        self._cb = self.tx_channel(2, value) if isinstance(value, str) else float(value)
        self._update_hue()

    @classmethod
    def tx_channel(cls, channel, value):
        """Translate channel string."""

        return float(value)
