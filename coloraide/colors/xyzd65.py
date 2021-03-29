"""XYZ D65 class."""
from ._space import RE_DEFAULT_MATCH
from ._gamut import GamutUnbound
from .xyz import XYZ
from . import _convert as convert
import re


class XYZD65(XYZ):
    """XYZ D65 class."""

    SPACE = "xyzd65"
    CHANNEL_NAMES = ("x", "y", "z", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D65"]

    _range = (
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0])
    )

    @classmethod
    def _to_xyz(cls, xyzd65):
        """To XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), xyzd65)

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return cls._chromatic_adaption(XYZ.white(), cls.white(), xyz)
