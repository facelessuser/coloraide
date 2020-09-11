"""HWB class."""
import re
from .base import _Color
from .tools import _ColorTools
from .. import util
from ..util import parse
from ..util import convert


class _HWB(_ColorTools, _Color):
    """HWB class."""

    SPACE = "hwb"
    DEF_BG = "color(hwb 0 0 0 / 1)"
    _MATCH = re.compile(
        r"(?xi)color\(\s*hwb\s+((?:{float}{sep}){{2}}{float}(?:{asep}{float})?)\s*\)".format(**parse.COLOR_PARTS)
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, _Color):
            self._ch, self._cw, self._cb = convert.convert(color.coords(), color.space(), self.space())
            self._alpha = color._alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._ch, self._cw, self._cb, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._ch = color[0]
            self._cw = color[1]
            self._cb = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    @property
    def _ch(self):
        """Hue channel."""

        return self._c1

    @_ch.setter
    def _ch(self, value):
        """Set hue channel."""

        self._c1 = value if 0.0 <= value <= 360.0 else value % 360.0

    @property
    def _cw(self):
        """Whiteness channel."""

        return self._c2

    @_cw.setter
    def _cw(self, value):
        """Set whiteness channel."""

        self._c2 = util.clamp(value, 0.0, 100.0)

    @property
    def _cb(self):
        """Blackness channel."""

        return self._c3

    @_cb.setter
    def _cb(self, value):
        """Set blackness channel."""

        self._c3 = util.clamp(value, 0.0, 100.0)

    def _grayscale(self):
        """Convert to grayscale."""

        factor = 1.0 / (self._cw + self._cb)
        self._c2 = self._cw + factor
        self._c3 = self._cb + factor

    def _mix(self, coords1, coords2, factor, factor2=1.0):
        """Blend the color with the given color."""

        if self._is_achromatic(coords1):
            coords1[0] = util.NAN
        if self._is_achromatic(coords2):
            coords2[0] = util.NAN
        self._ch = self._hue_mix_channel(coords1[0], coords2[0], factor, factor2)
        self._cw = self._mix_channel(coords1[1], coords2[1], factor, factor2)
        self._cb = self._mix_channel(coords1[2], coords2[2], factor, factor2)

    @property
    def hue(self):
        """Hue channel."""

        return self._ch

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._ch = self.tx_channel(1, value) if isinstance(value, str) else float(value)

    @property
    def whiteness(self):
        """Whiteness channel."""

        return self._cw

    @whiteness.setter
    def whiteness(self, value):
        """Set whiteness channel."""

        self._cw = self.tx_channel(2, value) if isinstance(value, str) else float(value)

    @property
    def blackness(self):
        """Blackness channel."""

        return self._cb

    @blackness.setter
    def blackness(self, value):
        """Set blackness channel."""

        self._cb = self.tx_channel(3, value) if isinstance(value, str) else float(value)

    @classmethod
    def tx_channel(cls, channel, value):
        """Translate channel string."""

        if channel == 0:
            return parse.norm_deg_channel(value)
        elif channel in (1, 2):
            return float(value)
        elif channel == -1:
            return float(value)
