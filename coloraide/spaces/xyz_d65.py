"""XYZ D65 class."""
from ..spaces import RE_DEFAULT_MATCH, GamutUnbound
from . import _cat
from .xyz import XYZ
import re


class XYZD65(XYZ):
    """XYZ D65 class."""

    SPACE = "xyz-d65"
    CHANNEL_NAMES = ("x", "y", "z", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = _cat.WHITES["D65"]

    RANGE = (
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0])
    )

    @classmethod
    def _to_xyz(cls, xyzd65):
        """To XYZ."""

        return _cat.chromatic_adaption(cls.white(), XYZ.white(), xyzd65)

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return _cat.chromatic_adaption(XYZ.white(), cls.white(), xyz)
