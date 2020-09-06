"""Colors."""
from .srgb import _SRGB
from .hsl import _HSL
from .hwb import _HWB
from .lab import _LAB
from .lch import _LCH

__all__ = ("SRGB", "HSL", "HWB", "LAB", "LCH")


class _ColorConvert:
    """A mix-in to allow converting between the various classes."""

    def convert(self, space):
        """Convert to color space."""

        obj = CS_MAP.get(space.lower())
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        return obj(self)

    def new(self, value, space=None):
        """Create new color in color space."""

        if space is None:
            space = self.space()

        obj = CS_MAP.get(space.lower())
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        return obj(value)


class SRGB(_ColorConvert, _SRGB):
    """RGB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class HSL(_ColorConvert, _HSL):
    """HSL color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class HWB(_ColorConvert, _HWB):
    """HWB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class LAB(_ColorConvert, _LAB):
    """HWB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class LCH(_ColorConvert, _LCH):
    """HWB color class."""

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


SUPPORTED = [HSL, HWB, LAB, LCH, SRGB]

CS_MAP = {}
for obj in SUPPORTED:
    CS_MAP[obj.space()] = obj
