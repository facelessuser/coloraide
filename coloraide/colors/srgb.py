"""SRGB color class."""
import re
from ._rgb import _RGBColor
from ..util import parse
from ..util import convert


class _SRGB(_RGBColor):
    """SRGB class."""

    SPACE = "srgb"
    DEF_BG = "color(srgb 0 0 0 / 1)"
    _MATCH = re.compile(
        r"(?xi)color\(\s*srgb\s+((?:{float}{sep}){{2}}{float}(?:{asep}{float})?)\s*\)".format(**parse.COLOR_PARTS)
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        self._c4 = 0.0
        super().__init__(color)
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

        super().mutate(obj)
        self._update_hue()

    def _mix(self, coords1, coords2, factor, factor2=1.0):
        """Blend the color with the given color."""

        super()._mix(coords1, coords2, factor, factor2)
        self._update_hue()

    @property
    def _ch(self):
        """Hue channel."""

        return self._c4

    @_ch.setter
    def _ch(self, value):
        """Set hue channel."""

        self._c4 = value if 0.0 <= value <= 360.0 else value % 360.0

    @property
    def red(self):
        """Adjust red."""

        return super().red

    @red.setter
    def red(self, value):
        """Adjust red."""

        super(_SRGB, self.__class__).red.fset(self, value)
        self._update_hue()

    @property
    def green(self):
        """Adjust green."""

        return super().green

    @green.setter
    def green(self, value):
        """Adjust green."""

        super(_SRGB, self.__class__).green.fset(self, value)
        self._update_hue()

    @property
    def blue(self):
        """Adjust blue."""

        return super().blue

    @blue.setter
    def blue(self, value):
        """Adjust blue."""

        super(_SRGB, self.__class__).blue.fset(self, value)
        self._update_hue()
