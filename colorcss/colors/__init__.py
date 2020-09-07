"""Colors."""
from .srgb import _SRGB
from .hsl import _HSL
from .hwb import _HWB
from .lab import _LAB
from .lch import _LCH

__all__ = ("SRGB", "HSL", "HWB", "LAB", "LCH")

CS_MAP = {}


class SRGB(_SRGB):
    """RGB color class."""

    spaces = CS_MAP

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class HSL(_HSL):
    """HSL color class."""

    spaces = CS_MAP

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class HWB(_HWB):
    """HWB color class."""
    spaces = CS_MAP

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class LAB(_LAB):
    """HWB color class."""

    spaces = CS_MAP

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


class LCH(_LCH):
    """HWB color class."""

    spaces = CS_MAP

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)


SUPPORTED = (HSL, HWB, LAB, LCH, SRGB)
for obj in SUPPORTED:
    CS_MAP[obj.space()] = obj
