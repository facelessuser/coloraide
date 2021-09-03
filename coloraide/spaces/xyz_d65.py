"""XYZ D65 class."""
from ..spaces import RE_DEFAULT_MATCH, GamutUnbound
from .xyz import XYZ
import re


class XYZD65(XYZ):
    """XYZ D65 class."""

    SPACE = "xyz-d65"
    SERIALIZE = ("--xyz-d65",)
    CHANNEL_NAMES = ("x", "y", "z", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    RANGE = (
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0]),
        GamutUnbound([0.0, 1.0])
    )

    @classmethod
    def _to_xyz(cls, parent, xyzd65):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, xyzd65)

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz)
