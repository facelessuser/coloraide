"""Colors."""
from .hsv import _HSV
from .srgb import _SRGB
from .hsl import _HSL
from .hwb import _HWB
from .lab import _LAB
from .lch import _LCH

__all__ = ("HSV", "SRGB", "HSL", "HWB", "LAB", "LCH")

CS_MAP = {}


class HSV(_HSV):
    """HSV color class."""

    spaces = CS_MAP

    def __init__(self, color=_HSV.DEF_BG):
        """Initialize."""

        super().__init__(color)


class SRGB(_SRGB):
    """RGB color class."""

    spaces = CS_MAP

    def __init__(self, color=_SRGB.DEF_BG):
        """Initialize."""

        super().__init__(color)


class HSL(_HSL):
    """HSL color class."""

    spaces = CS_MAP

    def __init__(self, color=_HSL.DEF_BG):
        """Initialize."""

        super().__init__(color)


class HWB(_HWB):
    """HWB color class."""

    spaces = CS_MAP

    def __init__(self, color=_HWB.DEF_BG):
        """Initialize."""

        super().__init__(color)


class LAB(_LAB):
    """HWB color class."""

    spaces = CS_MAP

    def __init__(self, color=_LAB.DEF_BG):
        """Initialize."""

        super().__init__(color)


class LCH(_LCH):
    """HWB color class."""

    spaces = CS_MAP

    def __init__(self, color=_LCH.DEF_BG):
        """Initialize."""

        super().__init__(color)


SUPPORTED = (HSV, HSL, HWB, LAB, LCH, SRGB)
for obj in SUPPORTED:
    CS_MAP[obj.space()] = obj
