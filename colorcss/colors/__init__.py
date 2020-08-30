"""Colors."""
from .srgb import _SRGB
from .hsl import _HSL
from .hwb import _HWB
from .lab import _LAB
from .lch import _LCH
from .util import convert

__all__ = ("SRGB", "HSL", "HWB", "LAB", "LCH")


class _ColorConvert:
    """A mix-in to allow converting between the various classes."""

    def convert(self, space):
        """Convert to color space."""

        obj = CS_MAP.get(space.lower())
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        return obj(self)

    def new(self, space, value):
        """Create new color in color space."""

        obj = CS_MAP.get(space.lower())
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        return obj(value)


class SRGB(_ColorConvert, _SRGB):
    """RGB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, SRGB):
            self._cr, self._cg, self._cb, self._alpha = color._cr, color._cg, color._cb, color._alpha
        elif isinstance(color, HSL):
            self._cr, self._cg, self._cb = convert.hsl_to_rgb(color._ch, color._cs, color._cl)
            self._alpha = color._alpha
        elif isinstance(color, HWB):
            self._cr, self._cg, self._cb = convert.hwb_to_rgb(color._ch, color._cw, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, LAB):
            self._cr, self._cg, self._cb = convert.lab_to_rgb(color._cl, color._ca, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, LCH):
            self._cr, self._cg, self._cb = convert.lch_to_rgb(color._cl, color._cc, color._ch)
            self._alpha = color._alpha
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.css_match(color)
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


class HSL(_ColorConvert, _HSL):
    """HSL color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, HSL):
            self._ch, self._cs, self._cl, self._alpha = color._ch, color._cs, color._cl, color._alpha
        elif isinstance(color, SRGB):
            self._ch, self._cs, self._cl = convert.rgb_to_hsl(color._cr, color._cg, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, HWB):
            self._ch, self._cs, self._cl = convert.hwb_to_hsl(color._ch, color._cw, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, LAB):
            self._ch, self._cs, self._cl = convert.lab_to_hsl(color._cl, color._ca, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, LCH):
            self._ch, self._cs, self._cl = convert.lch_to_hsl(color._cl, color._cc, color._ch)
            self._alpha = color._alpha
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.css_match(color)
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._ch, self._cs, self._cl, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._ch = color[0]
            self._cs = color[1]
            self._cl = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))


class HWB(_ColorConvert, _HWB):
    """HWB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, HWB):
            self._ch, self._cw, self._cb, self._alpha = color._ch, color._cw, color._cb, color._alpha
        elif isinstance(color, SRGB):
            self._ch, self._cw, self._cb = convert.rgb_to_hwb(color._cr, color._cg, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, HSL):
            self._ch, self._cw, self._cb = convert.hsl_to_hwb(color._ch, color._cs, color._cl)
            self._alpha = color._alpha
        elif isinstance(color, LAB):
            self._ch, self._cw, self._cb = convert.lab_to_hwb(color._cl, color._ca, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, LCH):
            self._ch, self._cw, self._cb = convert.lch_to_hwb(color._cl, color._cc, color._ch)
            self._alpha = color._alpha
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.css_match(color)
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


class LAB(_ColorConvert, _LAB):
    """HWB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, LAB):
            self._cl, self._ca, self._cb, self._alpha = color._cl, color._ca, color._cb, color._alpha
        elif isinstance(color, SRGB):
            self._cl, self._ca, self._cb = convert.rgb_to_lab(color._cr, color._cg, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, HSL):
            self._cl, self._ca, self._cb = convert.hsl_to_lab(color._ch, color._cs, color._cl)
            self._alpha = color._alpha
        elif isinstance(color, HWB):
            self._cl, self._ca, self._cb = convert.hwb_to_lab(color._ch, color._cw, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, LCH):
            self._cl, self._ca, self._cb = convert.lch_to_lab(color._cl, color._cc, color._ch)
            self._alpha = color._alpha
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.css_match(color)
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._cl, self._ca, self._cb, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._cl = color[0]
            self._ca = color[1]
            self._cb = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))


class LCH(_ColorConvert, _LCH):
    """HWB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, LCH):
            self._cl, self._cc, self._ch, self._alpha = color._cl, color._cc, color._ch, color._alpha
        elif isinstance(color, SRGB):
            self._cl, self._cc, self._ch = convert.rgb_to_lch(color._cr, color._cg, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, HSL):
            self._cl, self._cc, self._ch = convert.hsl_to_lch(color._ch, color._cs, color._cl)
            self._alpha = color._alpha
        elif isinstance(color, HWB):
            self._cl, self._cc, self._ch = convert.hwb_to_lch(color._ch, color._cw, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, LAB):
            self._cl, self._cc, self._ch = convert.lab_to_lch(color._cl, color._ca, color._cb)
            self._alpha = color._alpha
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.css_match(color)
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._cl, self._cc, self._ch, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._cl = color[0]
            self._cc = color[0]
            self._ch = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))


SUPPORTED = [HSL, HWB, LAB, LCH, SRGB]

CS_MAP = {}
for obj in SUPPORTED:
    CS_MAP[obj.get_colorspace()] = obj


def colorcss(string):
    """Parse a CSS color."""

    for colorspace in SUPPORTED:
        value = colorspace.css_match(string)
        if value is not None:
            obj = colorspace(value)
            return obj
    raise ValueError("'{}' doesn't appear to be a valid and/or supported CSS color".format(string))
